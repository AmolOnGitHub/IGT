"""
Utility / helper functions:
  - all_subsets          : enumerate every subset of a list of items
  - compute_demand       : bidder's demand bundle given personalized bundle prices
  - maximize_revenue     : find the revenue-maximising feasible allocation
  - bundle_key           : canonical string for a bundle (for logging/display)
  - compute_welfare      : total welfare of a final allocation
"""

from itertools import combinations


# Subset enumeration
def all_subsets(items):
    """
    Yield every subset (as frozenset) of `items`, including the empty set.

    Parameters
    ----------
    items : list
        Item identifiers (e.g. [1, 2, 3]).
    """
    for r in range(len(items) + 1):
        for combo in combinations(items, r):
            yield frozenset(combo)


# Demand computation (personalized bundle prices)
def compute_demand(valuation, bundle_prices):
    """
    Compute the demand bundle of a bidder given personalized bundle prices.

    The demand maximises:
        utility(S) = v_i(S) - p_i(S)

    The empty bundle always yields utility 0.
    If no non-empty bundle beats 0, the demand is ∅.

    Parameters
    ----------
    valuation    : dict  {frozenset -> float}
        v_i(S) for every bundle S.  Missing bundles default to 0.
    bundle_prices: dict  {frozenset -> float}
        p_i(S) for every bundle S.  Missing bundles default to 0.

    Returns
    -------
    frozenset   - the demand bundle D_i  (may be ∅)
    float       - the corresponding utility
    """
    best_utility = 0.0          # empty bundle -> utility 0
    best_bundle  = frozenset()

    # Iterate over every bundle that has a price entry or a valuation entry
    all_bundles = set(valuation.keys()) | set(bundle_prices.keys())

    for bundle in all_bundles:
        if not bundle:          # skip the empty bundle explicitly
            continue
        val   = valuation.get(bundle, 0.0)
        price = bundle_prices.get(bundle, 0.0)
        utility = val - price

        if utility > best_utility + 1e-9:
            best_utility = utility
            best_bundle  = bundle
        elif abs(utility - best_utility) < 1e-9 and bundle < best_bundle:
            # Tie-break: lexicographically smallest bundle for determinism
            best_bundle = bundle

    return best_bundle, best_utility


# Revenue-maximising feasible allocation
def maximize_revenue(items, prices, n_bidders):
    """
    Find the feasible allocation (T_1, …, T_n) that maximises total revenue
        sum_i  p_i(T_i)
    subject to:
        • T_i in M  for every i
        • T_i ∩ T_k = ∅  for i ≠ k          (items allocated at most once)
        • p_i(T_i) > 0  for any i with T_i ≠ ∅   (no zero-price allocation)

    Implemented via recursive backtracking (exact, suitable for small m, n).

    Parameters
    ----------
    items     : list[int]        all item ids
    prices    : dict {bidder_id -> {frozenset -> float}}
                personalized bundle prices  p_i(S)
    n_bidders : int

    Returns
    -------
    dict {bidder_id -> frozenset}   revenue-maximising allocation
    float                           corresponding total revenue
    """
    bidders = list(range(1, n_bidders + 1))

    best = {"revenue": -1.0, "alloc": {i: frozenset() for i in bidders}}

    def backtrack(bidder_idx, used_items, current_revenue, current_alloc):
        if bidder_idx == len(bidders):
            if current_revenue > best["revenue"] + 1e-9:
                best["revenue"] = current_revenue
                best["alloc"]   = dict(current_alloc)
            return

        i            = bidders[bidder_idx]
        free_items   = frozenset(items) - used_items
        i_prices     = prices[i]

        # Option A: bidder i gets nothing (T_i = ∅)
        current_alloc[i] = frozenset()
        backtrack(bidder_idx + 1, used_items, current_revenue, current_alloc)

        # Option B: bidder i gets some bundle S in free_items with p_i(S) > 0
        for bundle, price_val in i_prices.items():
            if not bundle:                          # skip empty bundle
                continue
            if price_val <= 1e-9:                  # no revenue → skip
                continue
            if not bundle.issubset(free_items):    # items already taken → skip
                continue
            current_alloc[i] = bundle
            backtrack(
                bidder_idx + 1,
                used_items | bundle,
                current_revenue + price_val,
                current_alloc,
            )

        current_alloc[i] = frozenset()  # restore for caller

    backtrack(0, frozenset(), 0.0, {i: frozenset() for i in bidders})
    return best["alloc"], best["revenue"]


# Logging / display helpers
def bundle_key(bundle):
    """
    Human-readable string for a bundle.

    Examples
    --------
    bundle_key(frozenset())       -> "∅"
    bundle_key(frozenset([1]))    -> "{1}"
    bundle_key(frozenset([1,2]))  -> "{1,2}"
    """
    if not bundle:
        return "∅"
    return "{" + ",".join(str(j) for j in sorted(bundle)) + "}"


def fmt_price(v):
    """Format a float price as int if it is whole, else as float."""
    return int(v) if v == int(v) else round(v, 4)


# Welfare
def compute_welfare(valuations, allocation):
    """
    Total social welfare  sum_i v_i(S_i).

    Parameters
    ----------
    valuations : dict {bidder_id -> {frozenset -> float}}
    allocation : dict {bidder_id -> frozenset}
    """
    return sum(
        valuations[i].get(allocation[i], 0.0)
        for i in allocation
    )
