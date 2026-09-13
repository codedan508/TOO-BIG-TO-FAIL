TOO BIG TO FAIL
VERSION 2 — PORTFOLIO INTELLIGENCE ENGINE
Updated September 13, 2026

OVERVIEW

TOO BIG TO FAIL traces institutional ownership through pension portfolios,
mutual funds, ETFs and the funds they hold. Its custom allocation engine
combines capital-weighted consensus, inverse company market caps and
recursive position limits to turn scattered financial disclosures into
a source-backed portfolio.

One click runs the complete pipeline: uncover underlying stocks, verify
exchange listings, measure institutional influence, adjust for company
size and calculate the final allocation. Every selected stock connects
back to the sources and numbers that put it in the portfolio.

WHAT CHANGED IN V2

V2 adds company-size weighting and a 15% maximum target for each stock.
Instead of stopping at institutional influence, the engine measures that
influence relative to company market cap. It then redistributes oversized
allocations proportionally until every stock fits within the 15% limit.

THE COMPLETE REBALANCE LOGIC

1. SCAN THE SOURCE UNIVERSE
Read the configured funds, ETFs and retirement portfolios. The current
universe includes 166 sources. Collect each source's reported assets and
two largest holdings. For pension filings, use disclosed securities value.
LIRPX remains excluded from the scan and asset total.

2. LOOK THROUGH EVERY FUND LAYER
When a top holding is another fund, open that fund's holdings and follow
its top two positions. Repeat through each layer until reaching individual
stocks or identified non-stock assets. Bonds, cash and property do not
receive stock votes. An unresolved holding is reported as an error.

3. WEIGHT EACH ORIGINAL SOURCE
Add the assets of all included source portfolios, then calculate:

    Source weight = source assets / total source assets

A source representing 10% of the total receives 10% influence. Assets of
funds discovered inside other funds are not added again. Source assets can
overlap; their sum measures model influence rather than unique capital.

4. COUNT COMPANY VOTES AND INFLUENCE
Each original source gives a company one vote and its full source weight.
Repeated appearances inside that source still count once. Configured
share-class aliases are combined into one company vote. SPY has no bonus.

    Company score = sum of the weights of sources containing the company

The score does not multiply by the stock's percentage inside each fund.

5. SELECT UP TO TEN STOCKS
Require at least three distinct source votes and a verified U.S. exchange
listing. U.S.-listed ADRs qualify; OTC-only securities do not.
Rank qualifying companies by their company score and select up to ten.
Break ties by company name, then company key.

Selection happens BEFORE the market-cap adjustment. Raw vote counts decide
whether a stock qualifies; weighted scores decide its selection ranking.

6. CALCULATE THE STARTING ALLOCATION

    Starting allocation = company score / total selected company scores

Convert this to percentages. Round to two decimal places while keeping
the combined starting allocation at exactly 100.00%.

7. FETCH COMPANY MARKET CAPS
Look up each selected company's market cap in U.S. dollars. Market cap is
the company's stock-market value, not its share price or a fund's assets.
Use the provider's company-level value, including its treatment of ADRs
and share classes. Save the source URL, valuation date and retrieval time.

8. ADJUST INFLUENCE FOR COMPANY SIZE

    Ratio score = starting allocation percentage / company market cap
    Ratio allocation = ratio score / sum of all selected ratio scores

For the same starting percentage, a smaller company gets a larger ratio.
For example, a stock starting at 0.82% can outrank one starting at 45.33%
if the second company is 1,000 times larger. The smaller company's ratio
would be about 18.09 times the larger company's ratio.

9. CAP AT 15% AND REDISTRIBUTE
Normalize the ratios to 100%. Set any allocation above 15% to 15%.
Redistribute the excess among stocks still below the cap, in proportion
to their ratio scores. Repeat if another stock crosses the limit.

Example: a stock assigned 25% keeps 15%. Its extra 10 percentage points
are shared proportionally among the uncapped stocks, not equally.

At least seven qualifying stocks are needed to invest 100% within this
limit. With six stocks, the maximum invested allocation is 90%; the
remaining 10% appears as unallocated cash. Final rounding keeps stocks
plus cash at exactly 100.00%.

10. SAVE THE COMPLETE RESULT
Apply the new allocation only after every required lookup and calculation
succeeds. If one fails, keep the previous allocation and scan timestamp,
show the failed lookup, and retain partial research separately.

The scanner verifies market-cap security identity, USD currency and a
valuation date within seven days. It does not silently reuse old market
caps or holdings to make an incomplete scan look successful.

HOW UPDATES WORK

The Rebalance button runs all ten steps again using fresh lookups.
Opening or refreshing the page displays the saved snapshot.
After more than one week without a complete successful scan, the app
shows a reminder to run the holdings scan.

Rebalancing is manual. There is no daily rebalancing or trade execution.
The 15% ceiling applies to calculated target weights; an actual portfolio's
weights can drift as prices change between updates.

INSPECT THE RESULTS

Sources: inspect fund assets, holdings trees, votes and reporting dates.
Stock details: inspect the starting allocation, company market cap,
market-cap source/date and final target percentage.
Export allocation: download the rules, source records, market caps and
calculated portfolio together as JSON.

PUBLIC DATA AND IMPLEMENTATION

Stock Analysis supplies configured fund holdings, most fund asset values
and company market caps. TIAA factsheets supply selected account assets.
13f.info supplies pension-filer disclosures. Nasdaq Trader directories
verify exchange listings. Exact source links are saved with the inputs.

Python handles scanning, recursive holdings resolution and allocation.
Flask serves the local application. HTML, CSS and JavaScript provide the
dark interface, scan progress, source inspection and exports.

LAUNCH FROM THE V2 PACKAGE

Extract the entire package and keep its files together.
Mac: double-click Start on Mac.command.
Windows: double-click Start on Windows.bat.

The launcher sets up dependencies, starts port 8765, waits for the server,
and opens http://127.0.0.1:8765 in the browser. Python 3.9 or newer must be
installed. Keep the terminal window open; press Ctrl+C to stop the server.
Rebalance requires internet access. The saved snapshot is available offline.
