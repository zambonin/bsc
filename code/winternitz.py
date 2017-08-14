#!/usr/bin/env python

import hashlib
from math import ceil, floor, log2
from random import getrandbits
from sys import argv


def chash(alg, msg, it):
    for _ in range(it):
        m = hashlib.new(alg)
        m.update(bytes(str(msg), 'utf-8'))
        msg = m.hexdigest()
    return msg


def keygen(alg, n):
    sk = [getrandbits(n) for _ in range(T)]
    pk = [chash(alg, i, 2**W - 1) for i in sk]
    return sk, pk


def getexp(alg, h):
    hmpad = [h[i:i+W] for i in range(0, T1 * W, W)]
    csum = sum(map(lambda x: (2**W - 1) - int(x, 2), hmpad))
    cpad = str(bin(csum)).replace('0b', int(T2 * W - log2(csum)) * '0')
    tcpad = [cpad[i:i+W] for i in range(0, T2 * W, W)]
    return list(map(lambda x: int(x, 2), hmpad + tcpad))


def sign(alg, h, key):
    return [chash(alg, k, p) for k, p in zip(key, getexp(alg, h))]


def verify(alg, h, key, s):
    missing = [(2**W - 1) - i for i in getexp(alg, h)]
    return all(chash(alg, si, pi) == k for pi, k, si in zip(missing, key, s))


if __name__ == '__main__':
    assert len(argv) == 3 and argv[1] in hashlib.algorithms_guaranteed

    _, alg, message = argv
    n = hashlib.new(alg).digest_size * 8
    h = bin(int(chash(alg, message, 1), 16))[2:].zfill(n)

    W = 16
    T1 = ceil(n / W)
    T2 = ceil((floor(log2(T1)) + 1 + W) / W)
    T = T1 + T2

    sk, pk = keygen(alg, n)
    s = sign(alg, h, sk)

    assert verify(alg, h, pk, s)
