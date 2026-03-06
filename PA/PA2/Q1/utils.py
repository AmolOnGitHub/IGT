"""
utils.py

Utility / helper functions shared across modules:
  - all_subsets      : enumerate every subset of a list of items
  - compute_demand   : find a bidder's demand set at given (modified) prices
  - bundle_key       : canonical string representation of a bundle (for logging)
  - compute_welfare  : total welfare of a final allocation
"""

from itertools import combinations


# Subset enumeration
def all_subsets(items):
    """
    Generate every subset (as a frozenset) of the given item list,
    including the empty set.

    Parameters
    ----------
    items : list
        The full list of item identifiers (e.g. [1, 2, 3]).

    Yields
    ------
    frozenset
        Each subset of `items`.
    """
    for r in range(len(items) + 1):
        for combo in combinations(items, r):
            yield frozenset(combo)


# Demand computation
def compute_demand(valuation, prices, current_alloc, epsilon):
    """
    Compute the demand set of a single bidder.

    For the ascending auction, a bidder i faces *modified* prices:
        p_j            for j already in their current allocation S_i  (no markup)
        p_j + epsilon  for j NOT in S_i                               (entry cost)

    The demand D_i is the bundle S that maximises:
        v_i(S) - sum_{j in S} modified_price_j

    Ties are broken by preferring the set that contains more items already in S_i (i.e., we try not to drop previously won items unnecessarily).

    Parameters
    ----------
    valuation    : dict  {frozenset -> float}
        Maps every bundle to its value for this bidder.
        Bundles absent from the dict are assumed to have value 0.
    prices       : dict  {item -> float}
        Current posted prices for every item.
    current_alloc: frozenset
        Items currently allocated to this bidder (S_i).
    epsilon      : float
        The price increment used as entry cost for items outside S_i.

    Returns
    -------
    frozenset
        The demand bundle D_i.
    """
    items = list(prices.keys())

    # Build modified price vector
    mod_prices = {}
    for j in items:
        if j in current_alloc:
            mod_prices[j] = prices[j]
        else:
            mod_prices[j] = prices[j] + epsilon

    best_utility = 0.0           # empty set always yields utility 0
    best_bundle  = frozenset()   # start with the empty-set as default demand

    for bundle in all_subsets(items):
        utility = valuation.get(bundle, 0) - sum(mod_prices[j] for j in bundle)
        if utility > best_utility + 1e-9:          # strictly better
            best_utility = utility
            best_bundle  = bundle
        elif abs(utility - best_utility) < 1e-9:   # tie-break: prefer bundle that keeps more items from current allocation
            if len(bundle & current_alloc) > len(best_bundle & current_alloc):
                best_bundle = bundle

    return best_bundle



# Logging helpers
def bundle_key(bundle):
    """
    Return a human-readable string for a bundle (frozenset of items).

    Examples
    --------
    bundle_key(frozenset())       -> "∅"
    bundle_key(frozenset([1]))    -> "{1}"
    bundle_key(frozenset([1,2]))  -> "{1,2}"
    """
    if not bundle:
        return "∅"
    return "{" + ",".join(str(j) for j in sorted(bundle)) + "}"



# Welfare
def compute_welfare(valuations, allocation):
    """
    Compute the total social welfare of a given allocation.

    Welfare = sum_i  v_i(S_i)

    Parameters
    ----------
    valuations : dict  {bidder_id -> {frozenset -> float}}
    allocation : dict  {bidder_id -> frozenset}

    Returns
    -------
    float
        Total welfare.
    """
    return sum(
        valuations[i].get(allocation[i], 0)
        for i in allocation
    )
