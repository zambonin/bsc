#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103,W0632,W1636

"""lamport.py

A simple Python implementation of the Lamport-Diffie one-time signature scheme,
arguably the earliest and simplest form of hash-based signatures."""

from __future__ import absolute_import
import hashlib
from random import getrandbits
from sys import argv


def _hash(t, _message):
    """Wrapper for hashlib's digest operations with a common base-16 output."""
    m = hashlib.new(t)
    m.update(bytes(str(_message), "utf-8"))
    return m.hexdigest()


def key_gen(_alg, _n):
    """Key generation algorithm. Generates `n` pairs of random numbers with `n`
    bits for the secret key. The public key consists of cryptographic hashes
    for those numbers."""
    _sk = [(getrandbits(_n), getrandbits(_n)) for _ in range(_n)]
    _pk = list(map(lambda x: (_hash(_alg, x[0]), _hash(_alg, x[1])), sk))
    return _sk, _pk


def sign(_h, _key):
    """Signature generation algorithm. Given a binary message of length `n`,
    for each bit of the message, choose the first or second number from each
    pair from the secret key if the bit is 0 or 1, respectively. Thus, the
    signature is half of the private key."""
    return [k[i] for k, i in zip(_key, map(int, _h))]


def verify(_h, _key, _s):
    """Signature verification algorithm. Hashes every number on the signature
    and compares the digests with the correct indices from the public key. The
    signature is valid if the comparison holds, and invalid otherwise."""
    l = [k[i] for k, i in zip(_key, map(int, _h))]
    ver = list(map(lambda x: _hash(alg, x), _s))
    return ver == l


if __name__ == "__main__":
    assert len(argv) == 3 and argv[1] in hashlib.algorithms_guaranteed

    _, alg, message = argv
    n = hashlib.new(alg).digest_size * 8
    h = bin(int(_hash(alg, message), 16))[2:].zfill(n)

    sk, pk = key_gen(alg, n)
    s = sign(h, sk)
    assert verify(h, pk, s)
