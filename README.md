# Limit Order Book Simulator

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Tests: 16 passed](https://img.shields.io/badge/pytest-16%20passed-green)](tests/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

A price–time-priority limit order book engine with synthetic order flow, plus a
microstructure study of spread, depth, book imbalance, and short-horizon price
moves. All data is **synthetic** (seeded RNG, no network).

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m lob_sim --n-events 2000 --seed 42 --levels 3 --horizon 10 --plot lob_study.png
python -m pytest tests/ -v
```

## Architecture / Method

**Engine** (`lob_sim/engine.py`) — `LimitOrderBook` stores bids/asks as
`price → FIFO deque` mappings. Matching follows **price–time priority**:

- A resting limit order that crosses the touch executes immediately against the
  best opposite level; any remainder rests on the book.
- A market order sweeps the opposite side level by level until filled or the
  book is empty (partial fill possible on a thin book).
- `cancel(order_id)` removes a resting order; `queue_position(order_id)`
  returns `(position_in_level, quantity_ahead)` with 1 = front of queue.

**Metrics** (`lob_sim/metrics.py`) — for best bid `b*`, best ask `a*`, and
top-`L` depths `B_L` (bid), `A_L` (ask):

- Spread: `s = a* − b*`
- Midprice: `m = (b* + a*) / 2`
- Book imbalance: `I_L = (B_L − A_L) / (B_L + A_L) ∈ [−1, 1]`
- Microprice (quantity-weighted, tilts toward the thin side):
  `M = (A_L·b* + B_L·a*) / (B_L + A_L)`
- Signed order flow: `+1` per buyer-initiated trade, `−1` per seller-initiated.
- Forward-return study: `r_{t,h} = (m_{t+h} − m_t) / m_t`, bucketed by the sign
  of `I_t`. Reported gap `= mean(r | I>0) − mean(r | I<0)`; a positive gap
  means imbalance predicts the direction of the short-term move.

**Flow** (`lob_sim/data.py`) — deterministic synthetic event stream
(45% limit bids / 45% limit asks / 7% market orders / 3% cancels, seeded
`numpy` RNG) against a pre-seeded 10-deep book. **Chart** (`lob_sim/viz.py`) —
midprice path, top-3 imbalance, and spread panels via matplotlib.

## Sample output (real run)

```bash
python -m lob_sim --n-events 2000 --seed 42 --levels 3 --horizon 10 --plot lob_study.png
```

```
events=2000 seed=42 trades=212
best_bid=99.95 best_ask=100.05 spread=0.1000 mid=100.0000
depth L3: bid=3969 ask=3852
imbalance(L3)=+0.015 microprice=100.0007
forward(h=10): n_pos=1798 n_neg=182 mean_ret_pos=+0.000000 mean_ret_neg=+0.000000 gap=+0.000000
chart -> lob_study.png
```

## Results

At this seed the book is balanced (`I_3 = +0.015`, microprice ≈ mid) and the
top of book never moves: seeded depth (5–50 per level) dwarfs market sweeps
(1–19), so forward returns are identically zero and the gap is exactly
`+0.000000`. The study machinery itself is validated by
`test_imbalance_predicts_direction_on_trended_series`, which recovers a
positive gap on a trended series — the zero here is a property of this
deep-book parameter set, not the metric. To see live imbalance dynamics,
thin the seed depth or enlarge market-order sizes in `data.py`.

## Limitations

- Synthetic flow only — no real exchange data, no latency, no fees, no hidden
  orders, no multi-venue fragmentation.
- Uniform RNG flow has no informed traders, volatility clustering, or
  intraday seasonality.
- Single instrument, fixed tick (0.05); no iceberg handling.

## Project structure

```
limit-order-book-simulator/
├── lob_sim/
│   ├── engine.py      # LimitOrderBook, Order/Trade, price-time priority matching
│   ├── metrics.py     # spread, midprice, imbalance, microprice, forward-return study
│   ├── data.py        # deterministic synthetic order flow (seeded RNG)
│   ├── viz.py         # matplotlib midprice / imbalance / spread chart
│   └── __main__.py    # CLI: run flow, print study, save chart
├── tests/
│   ├── test_engine.py   # matching, price/time priority, queue, cancels, sweeps
│   └── test_metrics.py  # imbalance, microprice, flow sign, study, determinism
├── requirements.txt
├── lob_study.png
├── LICENSE
└── README.md
```

## Testing

```bash
python -m pytest tests/ -v   # 16 passed, synthetic only, no network
```

Covers price priority (best level filled first), FIFO within a level,
queue-ahead quantities, cancel semantics, partial sweeps on thin books,
microprice tilt toward the thin side, and exact RNG determinism of the flow.

## License

MIT — see [LICENSE](LICENSE).
