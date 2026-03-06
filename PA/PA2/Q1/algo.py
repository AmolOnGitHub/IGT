"""
Item-price ascending auction for *substitutes* (gross-substitutes) valuations.

Algorithm (as defined in the assignment doc):
Initialization:
    For every item   j in M,   set p_j <- 0.
    For every bidder i,         set S_i <- null.

Repeat:
    For each bidder i compute demand D_i at modified prices:
        p_j           if j in S_i      (item already allocated to i, no markup)
        p_j + eps     if j not in S_i  (entry cost for new items)

    If S_i = D_i for ALL bidders -> exit loop.

    Pick the first bidder i with S_i != D_i and update:
        * For every j in D_i \\ S_i :  p_j <- p_j + epsilon  (raise new-item prices)
        * S_i <- D_i                                         (assign demand to i)
        * For every k != i :           S_k <- S_k \\ D_i     (remove i's items from others)

Output: allocation S_1, …, S_n   and welfare = \\sum_i v_i(S_i).
"""

from utils import compute_demand, bundle_key, compute_welfare


# Main algorithm
def ascending_auction(items, prices, allocations, valuations, epsilon, log_lines):
    """
    Run the item-price ascending auction.

    Parameters
    ----------
    items       : list[int]
        All item ids (1-indexed).
    prices      : dict {item_id: float}
        Initial prices — modified in place during the auction.
    allocations : dict {bidder_id: frozenset}
        Initial allocations (all null) — modified in place.
    valuations  : dict {bidder_id: dict{frozenset: float}}
        v[i][S] = value bidder i has for bundle S.
    epsilon     : float
        Price-increment step.  Must be > 0.
        For integer valuations epsilon = 1 is exact; smaller values give finer approximations but more iterations.
    log_lines   : list[str]
        Callers pass an empty list; the function appends human-readable log lines to it as the auction progresses.

    Returns
    -------
    allocation : dict {bidder_id: frozenset}
        Final allocation S_1, …, S_n  (same object as input `allocations`).
    welfare    : float
        Total social welfare of the final allocation.
    prices     : dict {item_id: float}
        Final prices (same object as input `prices`).
    """

    n_bidders = len(valuations)


    # Log header
    log_lines.append(f"Number of bidders: {n_bidders}")
    log_lines.append(f"Number of items:   {len(items)}")
    log_lines.append("")
    for i in range(1, n_bidders + 1):
        # Pretty-print the valuation dict (non-empty bundles only, sorted by size then items)
        def _bundle_display_key(s):
            sorted_ids = sorted(s)
            if all(x < 10 for x in sorted_ids):
                return "".join(str(x) for x in sorted_ids)   # "12" for {1,2}
            return ",".join(str(x) for x in sorted_ids)       # "1,10" for {1,10}

        entries = sorted(
            [(s, v) for s, v in valuations[i].items() if s],
            key=lambda kv: (len(kv[0]), sorted(kv[0]))
        )

        val_str = "{" + ", ".join(
            f'"{_bundle_display_key(s)}": {int(v) if v == int(v) else v}'
            for s, v in entries
        ) + "}"
        log_lines.append(f"Bidder {i} Valuation: {val_str}")
    log_lines.append("")


    # Iterative price-raising loop
    iteration = 0

    while True:
        iteration += 1
        log_lines.append(f"*** Iteration {iteration} ***")

        # Current item list and prices
        log_lines.append(f"Items:  {items}")
        log_lines.append(
            "Prices: [" +
            ", ".join(
                (str(int(prices[j])) if prices[j] == int(prices[j]) else str(prices[j]))
                for j in items
            ) + "]"
        )

        # Compute demands for all bidders
        demands = {}
        for i in range(1, n_bidders + 1):
            demands[i] = compute_demand(
                valuations[i], prices, allocations[i], epsilon
            )

        # Log demands
        log_lines.append("Bidder Demands:")
        for i in range(1, n_bidders + 1):
            log_lines.append(f"  Bidder {i}: {bundle_key(demands[i])}")

        # Log current allocation
        alloc_str = ",  ".join(
            f"S{i} = {bundle_key(allocations[i])}"
            for i in range(1, n_bidders + 1)
        )
        log_lines.append(f"Allocation:  {alloc_str}")
        log_lines.append("")

        # Termination check
        if all(allocations[i] == demands[i] for i in range(1, n_bidders + 1)):
            log_lines.append("Termination condition met: S_i = D_i for all bidders.")
            log_lines.append("")
            break

        # Find the first unsatisfied bidder
        for i in range(1, n_bidders + 1):
            if allocations[i] != demands[i]:
                Di = demands[i]
                new_items = Di - allocations[i]   # items entering i's bundle

                # Raise prices on newly acquired items
                if new_items:
                    price_changes = {j: prices[j] + epsilon for j in new_items}
                    for j in new_items:
                        prices[j] += epsilon
                    log_lines.append(
                        f"  Bidder {i}: S_{i}={bundle_key(allocations[i])} -> "
                        f"D_{i}={bundle_key(Di)}  (new items: {bundle_key(new_items)})"
                    )
                    log_lines.append(
                        "  Price updates: " +
                        ", ".join(
                            f"p_{j}: {prices[j]-epsilon:.0f} -> {prices[j]:.0f}"
                            for j in sorted(new_items)
                        )
                    )
                else:
                    log_lines.append(
                        f"  Bidder {i}: S_{i}={bundle_key(allocations[i])} -> "
                        f"D_{i}={bundle_key(Di)}  (no new items, bundle shrinks)"
                    )

                # Assign demand to bidder i
                allocations[i] = Di

                # Remove i's new bundle from all other bidders' allocations
                evicted = {}
                for k in range(1, n_bidders + 1):
                    if k != i:
                        before = allocations[k]
                        allocations[k] = allocations[k] - Di
                        removed = before - allocations[k]
                        if removed:
                            evicted[k] = removed

                if evicted:
                    evict_str = ",  ".join(
                        f"Bidder {k} loses {bundle_key(removed)}"
                        for k, removed in evicted.items()
                    )
                    log_lines.append(f"  Evictions: {evict_str}")

                log_lines.append("")
                break   # process one bidder per iteration, then recompute demands


    # Final output
    welfare = compute_welfare(valuations, allocations)

    log_lines.append("=" * 50)
    log_lines.append("Final Allocation:")
    for i in range(1, n_bidders + 1):
        log_lines.append(f"  S{i} = {bundle_key(allocations[i])}")
    log_lines.append(f"Final Prices:    " +
        ", ".join(f"p_{j}={prices[j]:.0f}" for j in items))
    log_lines.append(
        f"Welfare: {int(welfare) if welfare == int(welfare) else welfare}"
    )

    return allocations, welfare, prices
