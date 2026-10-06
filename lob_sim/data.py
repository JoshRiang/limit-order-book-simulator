"""Synthetic order-flow generator (deterministic with seed; no network)."""

from __future__ import annotations

import numpy as np

from lob_sim.engine import LimitOrderBook, Side


def run_simulation(n_events: int = 2000, seed: int = 42, base_price: float = 100.0) -> dict:
    """Generate random limit/market/cancel flow against a LimitOrderBook.

    Returns dict with book, snapshot/imbalance/midprice/spread histories,
    and trade-side list for flow analysis.
    """
    rng = np.random.default_rng(seed)
    book = LimitOrderBook()
    # seed the book with depth on both sides
    for i in range(10):
        book.add_limit(Side.BID, base_price - 0.05 * (i + 1), int(rng.integers(5, 50)))
        book.add_limit(Side.ASK, base_price + 0.05 * (i + 1), int(rng.integers(5, 50)))

    live_ids: list[int] = []
    snapshots, imbalances, mids, spreads = [], [], [], []
    trade_sides: list[str] = []

    from lob_sim.metrics import book_imbalance

    for _ in range(n_events):
        u = rng.random()
        ref = book.midprice() or base_price
        if u < 0.45:  # limit bid
            px = round(ref - float(rng.integers(1, 10)) * 0.05, 2)
            oid, _ = book.add_limit(Side.BID, px, int(rng.integers(1, 30)))
            live_ids.append(oid)
        elif u < 0.90:  # limit ask
            px = round(ref + float(rng.integers(1, 10)) * 0.05, 2)
            oid, _ = book.add_limit(Side.ASK, px, int(rng.integers(1, 30)))
            live_ids.append(oid)
        elif u < 0.97:  # market order
            side = Side.BID if rng.random() < 0.5 else Side.ASK
            fills = book.add_market(side, int(rng.integers(1, 20)))
            trade_sides.extend([t.aggressor_side.value for t in fills])
        else:  # cancel
            if live_ids:
                oid = live_ids.pop(int(rng.integers(0, len(live_ids))))
                book.cancel(oid)
        snap = book.snapshot(levels=3)
        snapshots.append(snap)
        imbalances.append(book_imbalance(book, levels=3) or 0.0)
        mids.append(book.midprice() or ref)
        spreads.append(book.spread() or 0.0)

    return {
        "book": book,
        "snapshots": snapshots,
        "imbalances": imbalances,
        "midprices": mids,
        "spreads": spreads,
        "trade_sides": trade_sides,
    }
