# Limit Order Book Simulator

Price–time-priority limit order book engine with synthetic order flow, plus a microstructure study of spread, depth, book imbalance, and short-horizon price moves. All data is synthetic (seeded RNG, no network).

`LimitOrderBook` stores bids/asks as `price → FIFO deque` mappings. Matching follows price–time priority: a resting limit order that crosses the touch executes immediately against the best opposite level (remainder rests); a market order sweeps the opposite side level by level until filled or the book is empty; `cancel(order_id)` removes a resting order; `queue_position(order_id)` returns `(position_in_level, quantity_ahead)` with 1 = front of queue. Metrics: spread, midprice, book imbalance `(B_L − A_L)/(B_L + A_L) ∈ [−1, 1]`, quantity-weighted microprice, signed order flow, and a forward-return study bucketed by imbalance sign. CLI simulates seeded flow (45% limit bids / 45% limit asks / 7% market orders / 3% cancels) against a pre-seeded 10-deep book, prints the imbalance/microprice/forward-return study, and saves a matplotlib chart.

```bash
git clone https://github.com/JoshRiang/limit-order-book-simulator.git
cd limit-order-book-simulator
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
python -m lob_sim --n-events 2000 --seed 42 --levels 3 --horizon 10 --plot lob_study.png
python -m pytest tests/ -v
```

```python
from lob_sim.engine import LimitOrderBook, Side, Trade
from lob_sim.metrics import spread, midprice, book_imbalance, microprice, imbalance_vs_forward_return

book = LimitOrderBook()
book.add_limit(Side.BID, 99.5, 10)
book.add_limit(Side.ASK, 100.5, 10)

print(f'Spread: {spread(book)}')           # 1.0
print(f'Midprice: {midprice(book)}')       # 100.0
print(f'Imbalance: {book_imbalance(book)}')# 0.0
print(f'Microprice: {microprice(book)}')   # 100.0

# Marketable limit order crosses immediately
oid, fills = book.add_limit(Side.BID, 100.5, 4)
print(f'Fills: {len(fills)}')              # 1

# Market sweep
fills = book.add_market(Side.BID, 100)
print(f'Filled qty: {sum(f.quantity for f in fills)}')

# Queue position
oid2, _ = book.add_limit(Side.BID, 99.0, 20)
pos, ahead = book.queue_position(oid2)    # (2, 10)
```

Project structure:

```
limit-order-book-simulator/
├── lob_sim/
│   ├── __init__.py     # exports: LimitOrderBook, Order, Side, Trade, spread, midprice, book_imbalance, microprice, depth_at_levels, signed_order_flow
│   ├── engine.py       # LimitOrderBook: price-time priority matching, limit/market orders, cancels, queue_position
│   ├── metrics.py      # spread, midprice, book_imbalance, microprice, depth_at_levels, signed_order_flow, imbalance_vs_forward_return
│   ├── data.py         # run_simulation: deterministic synthetic order flow (seeded RNG)
│   ├── viz.py          # plot_book_study: matplotlib midprice / imbalance / spread chart
│   └── __main__.py     # CLI: --n-events --seed --levels --horizon --plot
├── tests/
│   ├── test_engine.py  # matching, price/time priority, FIFO, queue-ahead, cancel, partial sweeps, invalid qty
│   └── test_metrics.py # imbalance, microprice tilt, flow sign, forward-return study on trended series, simulation determinism
├── requirements.txt    # numpy, pandas, matplotlib, pytest
├── LICENSE
└── README.md
```

Testing:

```bash
python -m pytest tests/ -v   # 16 passed, synthetic only, no network
```

License: MIT — see [LICENSE](LICENSE).

Author: Joshua Riangkamang — [github.com/JoshRiang](https://github.com/JoshRiang)
