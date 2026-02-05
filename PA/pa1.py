import sys
import re
import math
import numpy as np
import nashpy as nash
import warnings

warnings.filterwarnings("ignore")

def parse_payoffs(tokens, R, C):
    if len(tokens) < 2 * R * C:
        raise ValueError("Not enough payoff numbers: need 2*R*C numbers.")
    vals = tokens[:2 * R * C]
    A = np.zeros((R, C), dtype=float)
    B = np.zeros((R, C), dtype=float)
    idx = 0
    for i in range(R):
        for j in range(C):
            A[i, j] = vals[idx]; B[i, j] = vals[idx + 1]
            idx += 2
    return A, B

def eq_close(e1, e2, tol=1e-8):
    r1, c1 = e1; r2, c2 = e2
    return np.allclose(r1, r2, atol=tol, rtol=0) and np.allclose(c1, c2, atol=tol, rtol=0)

def main():
    data = sys.stdin.read().strip().splitlines()
    if len(data) < 3:
        sys.stderr.write("Error: expected at least 3 lines (R, C, payoffs)\n")
        sys.exit(1)

    try:
        R = int(data[0].strip())
        C = int(data[1].strip())
    except Exception:
        sys.stderr.write("Error: first two lines must be integers R and C\n")
        sys.exit(1)

    # join remaining lines and extract numbers
    rest = "\n".join(data[2:])  # this contains the payoff list (NFG format)
    tokens = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', rest)
    tokens = [float(t) for t in tokens]

    try:
        A, B = parse_payoffs(tokens, R, C)
    except ValueError as ve:
        sys.stderr.write(str(ve) + "\n")
        sys.exit(1)

    game = nash.Game(A, B)

    found = []
    max_labels = R + C
    for label in range(max_labels):
        try:
            eq = game.lemke_howson(initial_dropped_label=label)
        except Exception:
            continue
        rowp = np.asarray(eq[0], dtype=float)
        colp = np.asarray(eq[1], dtype=float)
        rowp = np.maximum(rowp, 0.0)
        colp = np.maximum(colp, 0.0)
        if rowp.sum() <= 0 or math.isnan(rowp.sum()):
            rowp = np.ones(R) / R
        else:
            rowp = rowp / rowp.sum()
        if colp.sum() <= 0 or math.isnan(colp.sum()):
            colp = np.ones(C) / C
        else:
            colp = colp / colp.sum()
        pair = (np.round(rowp, 12), np.round(colp, 12))
        duplicate = False
        for f in found:
            if eq_close(f, pair):
                duplicate = True
                break
        if not duplicate:
            found.append(pair)
        if len(found) >= (R + C):
            break

    print(len(found))
    for (r, c) in found:
        print(" ".join(str(float(x)) for x in r))
        print(" ".join(str(float(x)) for x in c))

if __name__ == "__main__":
    main()
