"""
(Q2 - Bundle-Price Ascending Auction)
Bundle-price ascending auction with personalized per-bundle prices.

Algorithm:
Initialization:
    For every bidder i and bundle S,  p_i(S) <- 0.

Repeat:
    1. Find allocation (T_1,...,T_n) that maximises revenue  sum_i p_i(T_i),
       subject to feasibility (disjoint bundles) and
       p_i(T_i) > 0 for every winner i  (zero-price bundles are not allocated).

    2. Let L = { i | T_i = ∅ }  be the set of losers.

    3. For every i in L compute demand  D_i = argmax_S { v_i(S) - p_i(S) }.

    4. If D_i = ∅ for all i in L, terminate.

    5. For every i in L with D_i != ∅ :  p_i(D_i) <- p_i(D_i) + epsilon.

Output: allocation T_1,...,T_n  and welfare = sum_i v_i(T_i).
"""

from utils import compute_demand, maximize_revenue, bundle_key, fmt_price, compute_welfare


# Main algorithm
def bundle_price_auction(items, prices, valuations, epsilon, log_lines):
    """
    Run the bundle-price ascending auction.

    Parameters
--
    items      : list[int]
        All item ids (1-indexed).
    prices     : dict {bidder_id -> {frozenset -> float}}
        Personalized bundle prices — modified *in place*.
        p_i(S) is the price bidder i pays for bundle S.
    valuations : dict {bidder_id -> {frozenset -> float}}
        v_i(S) = value bidder i has for bundle S.
    epsilon    : float
        Price increment (> 0).
    log_lines  : list[str]
        Caller passes an empty list; lines are appended here.

    Returns
---
    allocation : dict {bidder_id -> frozenset}
        Final allocation T_1,...,T_n.
    welfare    : float
        Total social welfare sum_i v_i(T_i).
    prices     : dict {bidder_id -> {frozenset -> float}}
        Final personalized bundle prices (same object as input).
    """
    n_bidders = len(valuations)
    bidders   = list(range(1, n_bidders + 1))


    # Log header - valuations
    log_lines.append(f"Number of bidders: {n_bidders}")
    log_lines.append(f"Number of items:   {len(items)}")
    log_lines.append("")

    for i in bidders:
        # Show only non-empty bundles with non-zero value, sorted by size
        def _bkey(s):
            sorted_ids = sorted(s)
            if all(x < 10 for x in sorted_ids):
                return "".join(str(x) for x in sorted_ids)
            return ",".join(str(x) for x in sorted_ids)

        entries = sorted(
            [(s, v) for s, v in valuations[i].items() if s and v != 0],
            key=lambda kv: (len(kv[0]), sorted(kv[0]))
        )
        val_str = (
            "{" +
            ", ".join(f'"{_bkey(s)}": {fmt_price(v)}' for s, v in entries) +
            "}"
        )
        log_lines.append(f"Bidder {i} Valuation: {val_str}")

    log_lines.append("")


    # Iterative price-raising loop
    iteration  = 0
    allocation = {i: frozenset() for i in bidders}   # current allocation

    while True:
        iteration += 1
        log_lines.append(f"*** Iteration {iteration} ***")
        log_lines.append(f"Items: {items}")

        # Step 1: revenue-maximising allocation
        allocation, revenue = maximize_revenue(items, prices, n_bidders)

        # Log allocation
        alloc_str = ",  ".join(
            f"T{i} = {bundle_key(allocation[i])}" for i in bidders
        )
        log_lines.append(f"Revenue-Maximising Allocation: {alloc_str}")
        log_lines.append(f"Total Revenue: {fmt_price(revenue)}")


        # Step 2: losers
        losers  = [i for i in bidders if not allocation[i]]
        winners = [i for i in bidders if     allocation[i]]

        log_lines.append(
            "Winners: " + (", ".join(f"Bidder {i}" for i in winners) or "none")
        )
        log_lines.append(
            "Losers:  " + (", ".join(f"Bidder {i}" for i in losers)  or "none")
        )

        # Log the current prices for losing bidders (non-zero entries only)
        for i in losers:
            non_zero = [
                f"p({bundle_key(s)})={fmt_price(p)}"
                for s, p in sorted(prices[i].items(), key=lambda kv: (len(kv[0]), sorted(kv[0])))
                if s and p > 1e-9
            ]
            if non_zero:
                log_lines.append(f"  Bidder {i} prices (non-zero): " + ",  ".join(non_zero))


        # Step 3: demands for losers
        demands = {}
        log_lines.append("Losers' Demands:")
        for i in losers:
            demand_bundle, utility = compute_demand(valuations[i], prices[i])
            demands[i] = demand_bundle
            log_lines.append(
                f"  Bidder {i}: D_{i} = {bundle_key(demand_bundle)}"
                + (f"  (utility = {fmt_price(utility)})" if demand_bundle else "")
            )


        # Step 4: termination check
        if all(demands[i] == frozenset() for i in losers):
            log_lines.append("")
            log_lines.append(
                "Termination: all losers have empty demand (D_i = ∅ for all i ∈ L)."
            )
            log_lines.append("")
            break


        # Step 5: raise prices for losers with non-empty demand
        log_lines.append("Price Updates:")
        for i in losers:
            Di = demands[i]
            if Di:
                old_price = prices[i].get(Di, 0.0)
                prices[i][Di] = old_price + epsilon
                log_lines.append(
                    f"  p_{i}({bundle_key(Di)}):  "
                    f"{fmt_price(old_price)} -> {fmt_price(prices[i][Di])}"
                )

        log_lines.append("")


    # Final output
    welfare = compute_welfare(valuations, allocation)

    log_lines.append("=" * 52)
    log_lines.append("Final Allocation:")
    for i in bidders:
        log_lines.append(f"  T{i} = {bundle_key(allocation[i])}")

    # Log final non-zero prices for each bidder
    log_lines.append("Final Prices (non-zero only):")
    for i in bidders:
        non_zero = [
            f"p({bundle_key(s)})={fmt_price(p)}"
            for s, p in sorted(prices[i].items(), key=lambda kv: (len(kv[0]), sorted(kv[0])))
            if s and p > 1e-9
        ]
        if non_zero:
            log_lines.append(f"  Bidder {i}: " + ",  ".join(non_zero))
        else:
            log_lines.append(f"  Bidder {i}: (all zero)")

    log_lines.append(
        f"Welfare: {fmt_price(welfare)}"
    )

    return allocation, welfare, prices
