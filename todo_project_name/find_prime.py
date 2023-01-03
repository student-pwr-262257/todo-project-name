import secrets
import random

def is_probable_prime(candidate: int) -> bool:
    """Check if `candidate` is a probable prime.

    Notes
    =====
    This function uses Rabin-Miller test under the hood.
    """
    primes =    {2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
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
                467, 479, 487, 491, 499, 503, 509}
    # Prime number cannot be less or equal to 1.
    if candidate <= 1:
        return False
    if candidate<=509:
        if candidate in primes:
            return True
        return False
    for number in primes:
        if candidate%number==0:
            return False
    return _rabin_miller(candidate=candidate, repeats=5)

def _rabin_miller(candidate: int, repeats: int = 30) -> bool:
    """Return the result of Rabin-Miller test.

    Returns True if test has been passed, and returns False otherwise.

    Parameters
    ==========
    candidate
    : tested natural number. Must be an odd natural number, greater than 2
    
    repeats
    : number of witnesses taken into account. Ensures that probability of
    false positive result is less than 4^(-repeats). Using a number greater
    than the candidate doesn't improve this.
    """
    if candidate % 2 == 0 or candidate <= 1:
        raise ValueError("`candidate` must be odd number greater than 2.")

    if repeats <= 0:
        raise ValueError("`repeats` must be positive.")

    # Witnesses, number of which is specified by `repeats`, are generated
    # from the interval containing no numbers greater, than `candidate`.
    repeats = min(candidate, repeats)

    #candidate-1==m*2^d for some positive integers m, d
    n = candidate.bit_length()
    m=candidate-1
    for i in range(1, n):
        m=m>>1
        if m & 1:
            d=i
            break
    visited=[]
    for _ in range(repeats):
        flag=False
        #rand a witness in range 2, 3, ..., candidate-1
        witness=random.randrange(2,candidate)
        while witness in visited:
            witness=random.randrange(2,candidate)
        visited.append(witness)
        tmp=pow(witness, m, candidate)
        if (tmp-1)%candidate==0:
            flag=True
        for i in range(d):
            if (tmp+1)%candidate==0:
                flag=True
            tmp=(tmp*tmp)%candidate
        if flag is False:
            return False
    return True

def find_prime(n:int)->int:
    """
    With high probability returns a n-bit prime number.
    """
    passed=False
    while passed is False:

        candidate=2**(n-1)+secrets.randbits(n-1)

        if is_probable_prime(candidate):
            passed=True
    return candidate
