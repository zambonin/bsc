#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103,W0632

"""winternitz.py

A simple Python implementation of the Winternitz one-time signature scheme,
a generalization of Lamport-Diffie and a building block for most hash-based
signature schemes."""

from __future__ import absolute_import, division
import hashlib
from math import ceil, floor, log2
from random import getrandbits
from sys import argv


def chash(_alg, msg, it):
    """Wrapper for hashlib's digest operations that hashes a piece of data
    repeatedly if needed."""
    dig = getattr(hashlib, _alg)
    for _ in range(it):
        msg = dig(bytes(str(msg), "utf-8")).hexdigest()
    return msg


def keygen(_alg, _n):
    """Key generation algorithm. Generates `T` random numbers with `n` bits for
    the secret key. The public key consists of each number's hash, taken
    `2**W - 1`  times."""
    sk = [getrandbits(_n) for _ in range(T)]
    pk = [chash(_alg, i, 2 ** W - 1) for i in sk]
    return sk, pk


def getexp(h):
    """Divides the message's hash in `T1` blocks of base-`W` numbers, with an
    additional `T2` blocks of checksum."""
    hmpad = [h[i : i + W] for i in range(0, T1 * W, W)]
    csum = sum(map(lambda x: (2 ** W - 1) - int(x, 2), hmpad))
    cpad = str(bin(csum)).replace("0b", int(T2 * W - log2(csum)) * "0")
    tcpad = [cpad[i : i + W] for i in range(0, T2 * W, W)]
    return list(map(lambda x: int(x, 2), hmpad + tcpad))


def sign(_alg, h, key):
    """Signature generation algorithm. Repeated hashes of each number in the
    secret key are taken in accordance with each base-`W` number calculated
    above."""
    exp = getexp(h)
    return [chash(_alg, k, p) for k, p in zip(key, exp)], exp


def verify(_alg, key, s, eee):
    """Signature verification algorithm. The base-`W` numbers are calculated
    again, and hashes are taken from the signature until the `2**W - 1`
    threshold. The final result is compared with the public key. The signature
    is valid if the comparison holds, and invalid otherwise."""
    missing = [(2 ** W - 1) - i for i in eee]
    return (
        all(chash(_alg, si, pi) == k for pi, k, si in zip(missing, key, s)),
        missing,
    )


def winternitz(_alg, _message):
    """Wrapper function for the whole algorithm that prints how many hashes are
    needed for signature generation and verification, for the message and
    checksum blocks."""
    h = bin(int(chash(_alg, _message, 1), 16))[2:].zfill(n)
    sk, pk = keygen(_alg, n)
    s, es = sign(_alg, h, sk)
    v, vs = verify(_alg, pk, s, es)
    print(
        sum(es[:T1]), sum(es[T1:]), sum(es), sum(vs[:T1]), sum(vs[T1:]), sum(vs)
    )
    assert v


if __name__ == "__main__":
    algs = hashlib.algorithms_guaranteed
    assert len(argv) == 4
    _, W, alg, message = argv

    W = int(argv[1])
    n = hashlib.new(alg).digest_size * 8
    T1 = ceil(n / W)
    T2 = ceil((floor(log2(T1)) + 1 + W) / W)
    T = T1 + T2
    winternitz(alg, message)
