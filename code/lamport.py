#!/usr/bin/env python

import hashlib
import random
from sys import argv

def _hash(t, message):
    m = hashlib.new(t)
    m.update(bytes(str(message), 'utf-8'))
    return m.hexdigest()

def key_gen(alg, n):
    sk = [(random.getrandbits(n), random.getrandbits(n)) for _ in range(n)]
    pk = list(map(lambda x: (_hash(alg, x[0]), _hash(alg, x[1])), sk))
    return sk, pk

def sign(h, key):
    return [k[i] for k, i in zip(key, map(int, h))]

def verify(h, key, s):
    l = [k[i] for k, i in zip(key, map(int, h))]
    ver = list(map(lambda x: _hash(alg, x), s))
    return ver == l

if __name__ == '__main__':
    assert len(argv) == 3 and argv[1] in hashlib.algorithms_guaranteed

    _, alg, message = argv
    n = hashlib.new(alg).digest_size * 8
    h = bin(int(_hash(alg, message), 16))[2:].zfill(n)

    sk, pk = key_gen(alg, n)
    s = sign(h, sk)
    assert verify(h, pk, s)
