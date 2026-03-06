"""
Entry point for the item-price ascending auction (Question 1).

Usage
-----
Run interactively (reads valuations from stdin):
    python main.py

Run in random mode (generates additive valuations for quick testing):
    python main.py --random [--seed SEED] [--max-val MAX_VAL]

Run with a pre-set custom example (edit CUSTOM_EXAMPLE at the bottom of
this file to inject specific valuations without touching algo / initialize):
    python main.py --custom

Input format (interactive mode)
Line 1 : number of items   n
Line 2 : number of bidders m
Line 3…: one JSON valuation object per bidder (see initialize.py for format)

Results are printed to stdout AND written to log.txt in the same directory.

The log records:
  • Initialised valuations
  • Per-iteration: prices, bidder demands, current allocations, price updates
  • Final allocation and social welfare
"""

import os
import argparse
from initialize import initialize_from_input, initialize_random, initialize_custom
from algo import ascending_auction

# Default epsilon (price increment)
EPSILON = 1

# ---------------------------------------------------------------------------
# Hardcoded custom example (edit here for grader/testing convenience)
#   bidder_id (int, 1-indexed) -> bundle_string -> value
#   bundle_string: concatenated single-char item ids ("12" = {1,2})
#                  or comma-separated multi-digit ids ("1,10" = {1,10})
# ---------------------------------------------------------------------------
CUSTOM_EXAMPLE = {
    "n_items"  : 2,
    "n_bidders": 2,
    "valuations": {
        1: {"1": 15, "2": 20, "12": 30},
        2: {"1": 10, "2": 25, "12": 30},
    }
}


# Helpers
def write_log(log_lines, path="log.txt"):
    """Write collected log lines to a file."""
    with open(path, "w") as f:
        f.write("\n".join(log_lines) + "\n")
    print(f"\n[Log written to {path}]")


def print_final(allocation, welfare, prices):
    """Pretty-print the final results to stdout."""
    print("\n" + "=" * 50)
    print("FINAL ALLOCATION")
    for i in sorted(allocation):
        items_str = (
            "{" + ",".join(str(j) for j in sorted(allocation[i])) + "}"
            if allocation[i] else "∅"
        )
        print(f"  Bidder {i}: S{i} = {items_str}")
    print(f"FINAL PRICES: { {j: int(p) if p == int(p) else p for j, p in prices.items()} }")
    print(f"WELFARE: {int(welfare) if welfare == int(welfare) else welfare}")
    print("=" * 50)



def main():
    parser = argparse.ArgumentParser(
        description="Item-price ascending auction for substitutes valuations."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--random", action="store_true",
        help="Auto-generate random additive valuations (satisfies gross substitutes)."
    )
    mode.add_argument(
        "--custom", action="store_true",
        help="Use the CUSTOM_EXAMPLE defined in main.py."
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed (only used with --random)."
    )
    parser.add_argument(
        "--max-val", type=int, default=50,
        help="Maximum per-item value in random mode (default: 50)."
    )
    parser.add_argument(
        "--epsilon", type=float, default=EPSILON,
        help=f"Price increment ε (default: {EPSILON})."
    )
    parser.add_argument(
        "--log", type=str, default="log.txt",
        help="Path for the output log file (default: log.txt)."
    )
    args = parser.parse_args()
    epsilon = args.epsilon


    # Initialisation
    if args.custom:
        # custom example hardcoded above
        n = CUSTOM_EXAMPLE["n_items"]
        m = CUSTOM_EXAMPLE["n_bidders"]
        print(f"[Custom mode]  n_items={n}, n_bidders={m}")
        items, prices, allocations, valuations = initialize_custom(
            n, m, CUSTOM_EXAMPLE["valuations"]
        )

    elif args.random:
        # random additive valuations
        # n and m are still read from stdin so the script stays testable
        print("Number of items n: ", end="", flush=True)
        n = int(input())
        print("Number of bidders m: ", end="", flush=True)
        m = int(input())
        print(f"[Random mode]  n_items={n}, n_bidders={m}, seed={args.seed}")
        items, prices, allocations, valuations = initialize_random(
            n, m, max_val=args.max_val, seed=args.seed
        )

    else:
        # interactive / file-redirected input
        # INPUT FORMAT:
        #   Line 1: n  (number of items)
        #   Line 2: m  (number of bidders)
        #   Next m lines: one JSON valuation dict per bidder
        #       Keys are bundle strings (e.g. "12" for {1,2}), values are integers.
        #       Bundles not listed are assumed to have value 0.

        print("Number of items n: ", end="", flush=True)
        n = int(input())
        print("Number of bidders m: ", end="", flush=True)
        m = int(input())
        items, prices, allocations, valuations = initialize_from_input(n, m)


    # Run the ascending auction
    log_lines = []
    log_lines.append(f"epsilon (price increment): {epsilon}")
    log_lines.append("")

    allocation, welfare, final_prices = ascending_auction(
        items, prices, allocations, valuations, epsilon, log_lines
    )


    # Output
    print("\n".join(log_lines))
    print_final(allocation, welfare, final_prices)

    # Determine log path relative to this file's directory
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.log)
    write_log(log_lines, log_path)


if __name__ == "__main__":
    main()
