"""
Handles initialization for the bundle-price ascending auction.

initialize_from_input(n_items, n_bidders)
    Read valuations interactively from stdin.

initialize_random(n_items, n_bidders, max_val=50, seed=None)
    Randomly generate submodular valuations for testing.

initialize_custom(n_items, n_bidders, raw_valuations)
    Build internal structures from a caller-supplied dict.

All three functions return the same triple:
    (items, prices, valuations)
"""

import json
import random
from utils import all_subsets


# Internal helpers
def _parse_bundle_dict(raw_dict, items):
    """
    Convert a JSON-style valuation dict into an internal dict keyed by frozenset.

    Key format
    ----------
    • Single-digit items  : concatenated  →  "12"    means {1, 2}
    • Multi-digit items   : comma-sep     →  "1,10"  means {1, 10}
    • Empty bundle        : not required (always 0)

    Fills in all subsets not listed with value 0.
    """
    item_set   = set(items)
    valuation  = {frozenset(): 0.0}

    for key, val in raw_dict.items():
        key = str(key).strip()
        if "," in key:
            ids = [int(x.strip()) for x in key.split(",")]
        else:
            ids = [int(c) for c in key]

        bundle = frozenset(ids)
        if not bundle.issubset(item_set):
            raise ValueError(
                f"Bundle {bundle} references items outside the item set {item_set}."
            )
        valuation[bundle] = float(val)

    # Fill remaining subsets with 0
    for subset in all_subsets(items):
        if subset not in valuation:
            valuation[subset] = 0.0

    return valuation


def _make_base_structures(n_items, n_bidders):
    """Return shared skeleton: items list, zero bundle prices, empty allocations."""
    items = list(range(1, n_items + 1))

    # Personalized bundle prices: p_i(S) = 0 for all i, S
    prices = {
        i: {bundle: 0.0 for bundle in all_subsets(items)}
        for i in range(1, n_bidders + 1)
    }
    return items, prices


# Option 1 - read from stdin
def initialize_from_input(n_items, n_bidders):
    """
    Read valuations interactively (or from a redirected file).

    Expected input format
    ---------------------
    One line per bidder — a JSON object mapping bundle strings to values.

    Bundle strings
    ~~~~~~~~~~~~~~
    • Single-digit items  : concatenate ids  →  "12"  means {1, 2}
    • Multi-digit items   : comma-separate   →  "1,10,2" means {1, 2, 10}
    • Unlisted bundles default to value 0.

    Example (2 items, 2 bidders):
        {"1":15,"2":20,"12":30}
        {"1":10,"2":25,"12":30}

    Prices
    ------
    All personalized bundle prices p_i(S) are initialized to 0.
    """
    items, prices = _make_base_structures(n_items, n_bidders)
    valuations    = {}

    print("Enter valuations for each bidder (one JSON object per line).")
    print(f"Items are numbered 1 to {n_items}.")
    print('Example: {"1":15,"2":20,"12":30}')

    for i in range(1, n_bidders + 1):
        while True:
            line = input(f"Bidder {i} valuation: ").strip()
            try:
                raw = json.loads(line)
                valuations[i] = _parse_bundle_dict(raw, items)
                break
            except (json.JSONDecodeError, ValueError) as e:
                print(f"  Invalid input ({e}). Please try again.")

    return items, prices, valuations


# Option 2 - random submodular valuations
def initialize_random(n_items, n_bidders, max_val=50, seed=None):
    """
    Generate random coverage (submodular) valuations for testing.

    Construction
    ------------
    Each bidder i is assigned a random weight w_{ij} ∈ [1, max_val] for each item j. The bundle value is then:

        v_i(S) = sum_{j in S}  w_{ij}  * r_{ij}

    where r_{ij} is a discount factor in [0.5, 1.0], sampled independently, modelling decreasing marginal returns (hence sub-additive / submodular).

    (Additive valuations are a special case with r_{ij} = 1 for all i, j, and trivially satisfy gross substitutes.
    Submodular valuations are more general and appropriate for bundle auctions.)

    Parameters
    ----------
    n_items   : int
    n_bidders : int
    max_val   : int    upper bound for per-item base values  (default 50)
    seed      : int|None  for reproducibility

    Returns
    -------
    (items, prices, valuations)
    """
    if seed is not None:
        random.seed(seed)

    items, prices = _make_base_structures(n_items, n_bidders)
    valuations    = {}

    for i in range(1, n_bidders + 1):
        # Per-item base value and discount factor for bidder i
        weights   = {j: random.randint(1, max_val) for j in items}
        discounts = {j: round(random.uniform(0.5, 1.0), 2) for j in items}

        val_dict = {}
        for bundle in all_subsets(items):
            val_dict[bundle] = float(
                sum(weights[j] * discounts[j] for j in bundle)
            )
        valuations[i] = val_dict

    return items, prices, valuations



# Option 3 - caller-supplied custom valuations
def initialize_custom(n_items, n_bidders, raw_valuations):
    """
    Build internal structures from caller-supplied valuations.

    This is the entry point used by graders / test scripts that want to inject
    specific valuations without touching any other code.

    Parameters
    ----------
    n_items        : int
    n_bidders      : int
    raw_valuations : dict  {bidder_id (1-indexed int):
                             dict {bundle_string: numeric_value}}

        Bundle-string format is the same as initialize_from_input:
            {"1": 15, "2": 20, "12": 30}   →  {1:15, {2}:20, {1,2}:30}

    Returns
    -------
    (items, prices, valuations)

    Notes
    -----
    All personalized bundle prices p_i(S) are initialized to 0.
    To set custom starting prices, modify the returned `prices` dict directly
    before passing it to the auction algorithm.
    """
    items, prices = _make_base_structures(n_items, n_bidders)
    valuations    = {}

    for i in range(1, n_bidders + 1):
        raw = raw_valuations.get(i, {})
        valuations[i] = _parse_bundle_dict(raw, items)

    return items, prices, valuations
