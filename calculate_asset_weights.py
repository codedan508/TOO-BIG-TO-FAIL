"""Recalculate fund influence and stock rankings from the saved asset snapshot."""
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'Asset Weight Inputs - 2026-09-13.json'
OUTPUT = ROOT / 'Asset Weighted Ranking - 2026-09-13.txt'


def calculate(data):
    rows = data['records']
    ids = [row['id'] for row in rows]
    assert len(ids) == len(set(ids)), 'Duplicate fund/plan IDs'
    assert all(row['assets_usd'] > 0 for row in rows), 'Missing or invalid assets'
    total = sum(Decimal(row['assets_usd']) for row in rows)
    weights = {row['id']: Decimal(row['assets_usd']) / total for row in rows}
    assert abs(sum(weights.values()) - 1) < Decimal('1e-24')
    backing = defaultdict(Decimal)
    contributors = defaultdict(list)
    for row in rows:
        assert len(row['stock_votes']) == len(set(row['stock_votes']))
        assert len(row['stock_votes']) <= 2
        for stock in row['stock_votes']:
            backing[stock] += Decimal(row['assets_usd'])
            contributors[stock].append(row['id'])
    ranking = sorted(backing, key=lambda stock: (-backing[stock], stock.casefold()))
    return total, weights, backing, contributors, ranking


def main():
    data = json.loads(INPUT.read_text())
    total, weights, backing, contributors, ranking = calculate(data)
    rows = data['records']
    eligibility = json.loads((ROOT / 'US Exchange Eligibility - 2026-09-13.json').read_text())
    eligible_ranking = [stock for stock in ranking if stock in eligibility['eligible']]
    assert len(eligible_ranking) >= 10
    lines = [
        'TOO BIG TO FAIL — ASSET-WEIGHTED FUND VOTES',
        f"Retrieved / calculated: {data['retrieved_date']}",
        f"Status: {data['status']}",
        '',
        f'Combined reported assets: ${total:,.0f} (approximately ${total / Decimal(1e12):.4f} trillion)',
        f'Valued fund/account/filer entries: {len(rows)}',
        f"Entries without explicit asset valuation date: {sum(row['asset_date'] is None for row in rows)}",
        'Fund weights sum to 100%. The SPY double-vote bonus is removed.',
        '',
        data['method'],
        '',
        'TOP TEN U.S. EXCHANGE-LISTED STOCKS BY WEIGHTED SCORE',
        eligibility['policy'],
        'Score = percent of the combined asset pool attached to records whose saved top two include the stock.',
        'Scores are NOT portfolio allocation percentages or actual stock ownership percentages.',
    ]
    for stock in eligible_ranking[:10]:
        rank = 1 + sum(backing[other] > backing[stock] for other in eligible_ranking)
        score = backing[stock] / total * 100
        listing = eligibility['eligible'][stock]
        lines.append(f"{rank}. {stock} ({listing['exchange']}: {listing['ticker']}): {score:.4f}% score; {len(contributors[stock])} contributing entries")
    lines += ['', 'EXCHANGE ELIGIBILITY SOURCES']
    for source in eligibility['sources']:
        lines.append(source['url'] + ' — ' + source['timestamp'])
    lines += ['Excluded from selection: ' + ', '.join(eligibility['excluded'])]
    lines += ['', 'FULL STOCK SCORE RANKING']
    for stock in ranking:
        rank = 1 + sum(backing[other] > backing[stock] for other in ranking)
        score = backing[stock] / total * 100
        lines.append(f'{rank}. {stock}: {score:.6f}%; supporting fund assets ${backing[stock]:,.0f}; entries: {", ".join(contributors[stock])}')
    lines += ['', 'ALL FUND / ACCOUNT / FILER WEIGHTS — LARGEST FIRST']
    for row in sorted(rows, key=lambda row: (-row['assets_usd'], row['id'])):
        lines += [
            '', row['id'] + ' — ' + row['name'],
            f"Reported assets: ${row['assets_usd']:,.0f}; weight: {weights[row['id']] * 100:.6f}%",
            'Asset valuation date: ' + (row['asset_date'] or 'Not explicitly provided; retrieved 2026-09-13'),
            'Asset source: ' + row['asset_source'],
            'Scope / source note: ' + row['asset_note'],
            'Saved direct holdings: ' + ('; '.join(row['holdings']) or 'No eligible stock pair recorded'),
            'Holdings source: ' + row['url'],
            'Eligible stock votes: ' + (', '.join(row['stock_votes']) or 'None'),
        ]
    lines += ['', 'LIMITATIONS AND COVERAGE'] + ['- ' + note for note in data['notes']]
    lines += ['', 'UNRESOLVED PLANS EXCLUDED FROM THIS RUN'] + ['- ' + name for name in data['excluded_unresolved']]
    lines += ['', 'LOCAL INPUT SOURCES'] + data['sources_files']
    lines += [INPUT.name, Path(__file__).name]
    OUTPUT.write_text('\n'.join(lines) + '\n')
    result = {
        'total_reported_assets_usd': int(total),
        'fund_weight_sum': str(sum(weights.values())),
        'ranked_stocks': [dict(stock=stock, score_pct=float(backing[stock] / total * 100), contributors=contributors[stock]) for stock in ranking],
        'fund_weights': {key: float(value) for key, value in weights.items()},
        'selection_policy': eligibility['policy'],
        'selected_top_10': [dict(stock=stock, score_pct=float(backing[stock] / total * 100), **eligibility['eligible'][stock]) for stock in eligible_ranking[:10]],
        'excluded_from_selection': eligibility['excluded'],
    }
    (ROOT / 'Asset Weight Results - 2026-09-13.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'Calculated {len(rows)} fund weights; sum = {sum(weights.values()):.12f}')
    print(f'Total reported assets: ${total:,.0f}')
    for stock in eligible_ranking[:10]:
        print(f'{stock}: {backing[stock] / total * 100:.4f}%')
    print(f'Saved: {OUTPUT}')


if __name__ == '__main__':
    main()
