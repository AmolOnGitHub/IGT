"""
Handles initialization for the item-price ascending auction.

initialize_from_input(n_items, n_bidders)
    Read valuations from stdin in the JSON-bundle format.

initialize_random(n_items, n_bidders, max_val=50, seed=None)
    Randomly generate *additive* valuations (additive => gross substitutes).

initialize_custom(n_items, n_bidders, raw_valuations)
    Build internal structures from a caller-supplied dict of dicts.

All three functions return the same triple:
    (items, prices, allocations, valuations)
"""

import json
import random
from itertools import combinations
from utils import all_subsets


# Internal helper
def _parse_bundle_dict(raw_dict, items):
    """
    Convert a JSON-style valuation dict (keys are concatenated item strings) into an internal dict keyed by frozenset.

    Example
    -------
    raw_dict = {"1": 15, "2": 20, "12": 30}
    items    = [1, 2]
    =>  { frozenset(): 0,
          frozenset({1}): 15,
          frozenset({2}): 20,
          frozenset({1,2}): 30 }

    The key "12" is interpreted as the bundle {1, 2} by splitting each characte* and matching against item ids converted to single-character strings.
    For item ids > 9 (two+ digits), the caller should pass keys as comma-separated strings, e.g. "1,10,2" => {1, 2, 10}.
    """

    item_set = set(items)
    valuation = {frozenset(): 0.0}   # empty bundle always valued at 0

    for key, val in raw_dict.items():
        key = str(key).strip()

        # Support both "12" (single-digit items) and "1,2,10" (multi-digit)
        if "," in key:
            ids = [int(x.strip()) for x in key.split(",")]
        else:
            ids = [int(c) for c in key]

        bundle = frozenset(ids)

        # Validate that all ids are known items
        if not bundle.issubset(item_set):
            raise ValueError(
                f"Bundle {bundle} references items not in the item set {item_set}."
            )
        valuation[bundle] = float(val)

    # Ensure every subset that was NOT specified explicitly gets value 0
    for subset in all_subsets(items):
        if subset not in valuation:
            valuation[subset] = 0.0

    return valuation


def _make_base_structures(n_items, n_bidders):
    """Return the shared skeleton: items list, zero prices, empty allocations."""
    items       = list(range(1, n_items + 1))
    prices      = {j: 0.0 for j in items}
    allocations = {i: frozenset() for i in range(1, n_bidders + 1)}
    return items, prices, allocations



# Option 1 – read from stdin
def initialize_from_input(n_items, n_bidders):
    """
    Read valuations interactively (or from a redirected file).

    Expected input format
    One line per bidder.  Each line is a JSON object whose keys are bundle strings and values are numeric valuations.

    Bundle strings:
    • Single-digit items  : concatenate ids  →  "12"  means {1, 2}
    • Multi-digit items   : comma-separate   →  "1,10,2" means {1, 2, 10}
    • Empty bundle need not be listed (defaults to 0).

    Example (2 items, 2 bidders)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    {"1":15,"2":20,"12":30}
    {"1":10,"2":25,"12":30}
    """
    items, prices, allocations = _make_base_structures(n_items, n_bidders)
    valuations = {}

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

    return items, prices, allocations, valuations



# Option 2 – random additive valuations (satisfies gross-substitutes)
def initialize_random(n_items, n_bidders, max_val=50, seed=None):
    """
    Generate random additive valuations.

    Additive valuations trivially satisfy the gross-substitutes condition:
        v_i(S) = sum_{j in S} w_{ij}
    where w_{ij} is bidder i's private value for individual item j,
    drawn uniformly from [1, max_val].

    Parameters
    ----------
    n_items    : int
    n_bidders  : int
    max_val    : int   upper bound for per-item values (default 50)
    seed       : int|None  for reproducibility

    Returns
    -------
    (items, prices, allocations, valuations)
    """
    if seed is not None:
        random.seed(seed)

    items, prices, allocations = _make_base_structures(n_items, n_bidders)
    valuations = {}

    for i in range(1, n_bidders + 1):
        # Draw a per-item weight for bidder i
        weights = {j: random.randint(1, max_val) for j in items}
        val_dict = {}
        for bundle in all_subsets(items):
            val_dict[bundle] = float(sum(weights[j] for j in bundle))
        valuations[i] = val_dict

    return items, prices, allocations, valuations



# Option 3 – caller-supplied custom valuations
def initialize_custom(n_items, n_bidders, raw_valuations):
    """
    Build internal structures from caller-supplied valuations.

    This is the entry point used to inject specific valuations without touching any other code.

    Parameters
    ----------
    n_items        : int
    n_bidders      : int
    raw_valuations : dict  {bidder_id (1-indexed int):
                             dict {bundle_string: numeric_value}}

        bundle_string format is the same as for initialize_from_input:
        e.g. {1: {"1": 15, "2": 20, "12": 30}, 2: {"1": 10, "12": 30}}

    Returns
    -------
    (items, prices, allocations, valuations)
    """
    items, prices, allocations = _make_base_structures(n_items, n_bidders)
    valuations = {}

    for i in range(1, n_bidders + 1):
        raw = raw_valuations.get(i, {})
        valuations[i] = _parse_bundle_dict(raw, items)

    return items, prices, allocations, valuations
