#!/usr/bin/env python

import hashlib
from datetime import datetime
from math import ceil, floor, log2
from random import getrandbits
from sys import argv


def chash(alg, msg, it):
    dig = getattr(hashlib, alg)
    for _ in range(it):
        msg = dig(bytes(str(msg), 'utf-8')).hexdigest()
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


def winternitz(alg, message):
    h = bin(int(chash(alg, message, 1), 16))[2:].zfill(n)
    sk, pk = keygen(alg, n)
    s = sign(alg, h, sk)

    assert verify(alg, h, pk, s)


if __name__ == '__main__':
    algs = hashlib.algorithms_guaranteed
    assert len(argv) == 2
    _, message = argv

    W = 16
    for alg in sorted(filter(lambda x: 'shake' not in x, algs)):
        start = datetime.now()
        n = hashlib.new(alg).digest_size * 8
        T1 = ceil(n / W)
        T2 = ceil((floor(log2(T1)) + 1 + W) / W)
        T = T1 + T2
        winternitz(alg, message)
        end = datetime.now()
        print("{:10} {}".format(alg, end - start))
