import secrets
from core import mod_exp
import random

def rabin_miller(candidate:int, repeats:int = 30)->bool:
    """
    Function implements Rabin-Miller primality test. 
    Returns True if test has been passed, and returns False otherwise.
    Arguments:
    -candidate -- tested natural number. Must be larger than repeats+2,
    -repeats   -- number of witnesses taken into account. Ensures that 
                probability of false positive result is less than 4^(-repeats).
    """
    if(candidate<repeats+2):
        raise ValueError("candidate must be larger than repeats+2")
    #candidate-1==m*2^d for some positive integers m, d
    n=len(bin(candidate)[2:])
    m=candidate-1
    d=1
    tmp=m/2
    for i in range(1, n):
        m=tmp
        tmp=m/2
        if tmp!=int(tmp):
            d=i
            m=int(m)
            break
    visited=[]
    for _ in range(repeats):
        flag=False
        #rand a witness in range 2, 3, ..., candidate-1
        witness=random.randrange(2,candidate)
        while witness in visited:
            witness=random.randrange(2,candidate)
        visited.append(witness)
        tmp=mod_exp(witness, m, candidate)
        if (tmp-1)%candidate==0:
            flag=True
        for i in range(d):
            if (tmp+1)%candidate==0:
                flag=True
            tmp=tmp*2
        if flag is False:
            return False
    return True

def find_prime(n:int)->int:
    """
    With high probability returns a n-bit prime number.
    """
    first_primes =  [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
                    31, 37, 41, 43, 47, 53, 59, 61, 67,
                    71, 73, 79, 83, 89, 97, 101, 103,
                    107, 109, 113, 127, 131, 137, 139,
                    149, 151, 157, 163, 167, 173, 179,
                    181, 191, 193, 197, 199, 211, 223,
                    227, 229, 233, 239, 241, 251, 257,
                    263, 269, 271, 277, 281, 283, 293,
                    307, 311, 313, 317, 331, 337, 347, 
                    349, 353, 359, 367, 373, 379, 383, 
                    389, 397, 401, 409,	419, 421, 431, 
                    433, 439, 443, 449, 457, 461, 463, 
                    467, 479, 487, 491, 499, 503, 509, 
                    521, 523, 541, 547, 557, 563, 569, 
                    571, 577, 587, 593, 599, 601, 607, 
                    613, 617, 619, 631, 641, 643, 647, 
                    653, 659, 661, 673, 677, 683, 691, 
                    701, 709, 719, 727, 733, 739, 743, 
                    751, 757, 761, 769, 773, 787, 797, 809]
    passed=False
    while passed is False:
        flag=True
        candidate=2**(n-1)+secrets.randbits(n-1)
        if candidate<=first_primes[-1]:
            if candidate in first_primes:
                return candidate
            continue
        for number in first_primes:
            if candidate%number==0:
                flag=False
        if flag is False:
            continue

        if rabin_miller(candidate,5):
            passed=True
    return candidate
