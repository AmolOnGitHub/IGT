"""
Entry point for the bundle-price ascending auction.

Usage
-----
Run interactively (reads valuations from stdin):
    python main.py

Run in random mode (generates submodular valuations for quick testing):
    python main.py --random [--seed SEED] [--max-val MAX_VAL]

Run with a pre-set custom example (edit CUSTOM_EXAMPLE below):
    python main.py --custom

Input format (interactive / redirected mode)
--------------------------------------------
Line 1 : number of items   n
Line 2 : number of bidders m
Lines 3…m+2 : one JSON valuation object per bidder

    Keys   : bundle strings  ("12" = {1,2},  "1,10" = {1,10})
    Values : numeric valuations
    Unlisted bundles default to 0.

Output
------
Results are printed to stdout AND written to log.txt in the working directory.

Log contents
------------
  1. Initialized valuations
  2. Per iteration: revenue-maximising allocation, winners/losers,
     current prices, losers' demands, price updates
  3. Final allocation and welfare
"""

import os
import argparse
from initialize import initialize_from_input, initialize_random, initialize_custom
from algo import bundle_price_auction


# Default epsilon
EPSILON = 1


# Custom example – edit here to inject specific valuations without touching
# algo.py or initialize.py
#   bidder_id (int, 1-indexed) → bundle_string → value
#   "12" = bundle {1,2};   "1,10" = bundle {1,10}  (for items > 9)
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
    """Write the collected log lines to a file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print(f"\n[Log written to {path}]")


def print_final(allocation, welfare, prices):
    """Pretty-print the final allocation and welfare to stdout."""
    print("\n" + "=" * 52)
    print("FINAL ALLOCATION")
    for i in sorted(allocation):
        bundle = allocation[i]
        label  = (
            "{" + ",".join(str(j) for j in sorted(bundle)) + "}"
            if bundle else "∅"
        )
        print(f"  Bidder {i}: T{i} = {label}")
    print(f"WELFARE: {round(welfare, 4) if welfare != int(welfare) else int(welfare)}")
    print("=" * 52)


# Main
def main():
    parser = argparse.ArgumentParser(
        description="Bundle-price ascending auction (Q2)."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--random", action="store_true",
        help="Auto-generate random submodular valuations for testing."
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
        help="Maximum per-item base value in random mode (default: 50)."
    )
    parser.add_argument(
        "--epsilon", type=float, default=EPSILON,
        help=f"Price increment epsilon (default: {EPSILON})."
    )
    parser.add_argument(
        "--log", type=str, default="log.txt",
        help="Path for the output log file (default: log.txt)."
    )
    args    = parser.parse_args()
    epsilon = args.epsilon


    # Initialisation
    if args.custom:
        n = CUSTOM_EXAMPLE["n_items"]
        m = CUSTOM_EXAMPLE["n_bidders"]
        print(f"[Custom mode]  n_items={n}, n_bidders={m}")
        items, prices, valuations = initialize_custom(
            n, m, CUSTOM_EXAMPLE["valuations"]
        )

    elif args.random:
        # n and m are read from stdin so the script is easy to test
        print("Number of items n: ", end="", flush=True)
        n = int(input())
        print("Number of bidders m: ", end="", flush=True)
        m = int(input())
        print(f"[Random mode]  n_items={n}, n_bidders={m}, seed={args.seed}")
        items, prices, valuations = initialize_random(
            n, m, max_val=args.max_val, seed=args.seed
        )

    else:
        # interactive / file-redirected input
        # INPUT FORMAT:
        #   Line 1 : n   (number of items, integer)
        #   Line 2 : m   (number of bidders, integer)
        #   Lines 3..m+2: one JSON valuation dict per bidder
        #       Keys   = bundle strings ("12" for {1,2}, "1,10" for {1,10})
        #       Values = integer or float valuations
        #       Bundles not listed default to 0.

        print("Number of items n: ", end="", flush=True)
        n = int(input())
        print("Number of bidders m: ", end="", flush=True)
        m = int(input())
        items, prices, valuations = initialize_from_input(n, m)


    # Run auction
    log_lines = []
    log_lines.append(f"epsilon (price increment): {epsilon}")
    log_lines.append("")

    allocation, welfare, final_prices = bundle_price_auction(
        items, prices, valuations, epsilon, log_lines
    )


    # Output
    print("\n".join(log_lines))
    print_final(allocation, welfare, final_prices)

    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.log)
    write_log(log_lines, log_path)


if __name__ == "__main__":
    main()
