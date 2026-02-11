import sys
import numpy as np

def LemkeHowson(*args):
    """    
    Syntax:
      nashEqbm = LEMKEHOWSON(A, B)
      nashEqbm = LEMKEHOWSON(A, B, k0)
      nashEqbm = LEMKEHOWSON(A, B, k0, maxPivots)
    """
    
    if len(args) < 2 or len(args) > 4:
        raise ValueError('This function takes between two and four arguments')
    
    A = args[0]
    B = args[1]
    
    if np.any(np.array(A.shape) != np.array(B.shape)):
        raise ValueError('Matrices must have same dimension')
    
    m, n = A.shape
    size_ = [m, n]
    
    if len(args) > 2:
        k0 = args[2]
        if k0 < 1 or k0 > m+n:
            raise ValueError(f'Initial pivot must be in {{1,...,{n+m}}}')
    else:
        k0 = 1
    
    if len(args) == 4:
        maxPivots = args[3]
        if maxPivots < 1:
            raise ValueError('Maximum pivots parameter must be a positive integer!')
    else:
        maxPivots = 500000
    
    minVal = min(np.min(A), np.min(B))
    if minVal <= 0:
        A = A + np.ones(A.shape) * (1 - minVal)
        B = B + np.ones(A.shape) * (1 - minVal)
    
    Tab = [None, None]
    Tab[0] = np.hstack([B.T, np.eye(n), np.ones((n, 1))])
    Tab[1] = np.hstack([np.eye(m), A, np.ones((m, 1))])
    
    rowLabels = [None, None]
    rowLabels[0] = list(range(m+1, m+n+1))
    rowLabels[1] = list(range(1, m+1))
    
    k = k0
    player = 1 if k0 <= m else 2
    
    numPiv = 0
    while numPiv < maxPivots:
        numPiv += 1
        LP = Tab[player - 1]
        m_, _ = LP.shape
        
        max_ = 0
        ind = -1
        for i in range(m_):
            t = LP[i, k-1] / LP[i, m+n]
            if t > max_:
                ind = i
                max_ = t
        
        if max_ > 0:
            Tab[player - 1] = pivot(LP, ind, k)
        else:
            break
        
        temp = rowLabels[player - 1][ind]
        rowLabels[player - 1][ind] = k
        k = temp
        
        if k == k0:
            break
        
        player = 2 if player == 1 else 1
    
    if numPiv == maxPivots:
        raise RuntimeError(f'Maximum pivot steps ({maxPivots}) reached!')
    
    nashEqbm = [None, None]
    
    for player in range(1, 3):
        x = np.zeros(size_[player - 1])
        rows = rowLabels[player - 1]
        LP = Tab[player - 1]
        
        for i in range(len(rows)):
            if player == 1 and rows[i] <= size_[0]:
                x[rows[i] - 1] = LP[i, m+n] / LP[i, rows[i] - 1]
            elif player == 2 and rows[i] > size_[0]:
                x[rows[i] - size_[0] - 1] = LP[i, m+n] / LP[i, rows[i] - 1]
        
        nashEqbm[player - 1] = x / np.sum(x)
    
    return nashEqbm


def pivot(A, r, s):
    m, _ = A.shape
    B = A.copy()
    for i in range(m):
        if i != r:
            B[i, :] = A[i, :] - A[i, s-1] / A[r, s-1] * A[r, :]
    return B


def parse_nfg(R, C, data):
    A = np.zeros((R, C))
    B = np.zeros((R, C))
    idx = 0
    for i in range(R):
        for j in range(C):
            A[i, j] = data[idx]
            B[i, j] = data[idx + 1]
            idx += 2
    return A, B


def same_equilibrium(eq1, eq2, tol=1e-6):
    return np.allclose(eq1[0], eq2[0], atol=tol) and \
           np.allclose(eq1[1], eq2[1], atol=tol)


def main():
    data = sys.stdin.read().strip().split()
    ptr = 0

    R = int(data[ptr]); ptr += 1
    C = int(data[ptr]); ptr += 1

    payoff_count = 2 * R * C
    payoffs = list(map(float, data[ptr:ptr + payoff_count]))

    A, B = parse_nfg(R, C, payoffs)

    equilibria = []

    for k0 in range(1, R + C + 1):
        try:
            eq = LemkeHowson(A, B, k0)
            duplicate = False
            for e in equilibria:
                if same_equilibrium(eq, e):
                    duplicate = True
                    break
            if not duplicate:
                equilibria.append(eq)
            if len(equilibria) == R + C:
                break
        except:
            pass

    print(len(equilibria))
    for x, y in equilibria:
        print(" ".join(f"{v:.6f}" for v in x))
        print(" ".join(f"{v:.6f}" for v in y))


if __name__ == "__main__":
    main()
