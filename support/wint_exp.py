#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0330,W0632

"""wint_exp.py

Proof-of-concept implementations of optimizations suggested for the Winternitz
one-time signature scheme. Used by `gen_tables.sh`."""

from __future__ import absolute_import, division
import hashlib
from math import ceil, floor, log2
from os import urandom
from typing import List, Tuple
from sys import argv


def t1(m: int, w: int) -> int:
    """Number of blocks that the message hash will take."""
    return ceil(m / w)


def t2(m: int, w: int) -> int:
    """Number of blocks that the checksum will take."""
    return ceil((floor(log2(t1(m, w))) + 1 + w) / w)


def nc(m: int, w: int) -> int:
    """Number of bits used by the checksum value."""
    return ceil(log2(t1(m, w) * 2 ** w - 1))


def nu(m: int, w: int) -> int:
    """Number of unused bits on the `T2` blocks."""
    return t2(m, w) * w - nc(m, w)


def b1(_alg: str, msg: str, m: int, w: int) -> List[int]:
    """Base-`W` values for the `T1` blocks."""
    digest = bin(int(chash(_alg, msg, 1), 16))[2:].zfill(m)
    split = [digest[j : j + w] for j in range(0, t1(m, w) * w, w)]
    return list(map(lambda x: int(x, 2), split))


def b2(exp: List[int], m: int, w: int, pad: bool = False) -> List[int]:
    """Base-`W` values for the `T2` blocks."""
    csum = sum(map(lambda x: (2 ** w - 1) - x, exp))
    flip = int(t2(m, w) * w - log2(csum)) * str(int(pad))
    cpad = str(bin(csum)).replace("0b", flip)
    tcpad = [cpad[i : i + w] for i in range(0, t2(m, w) * w, w)]
    return list(map(lambda x: int(x, 2), tcpad))


def chash(_alg: str, msg: str, it: int) -> str:
    """Wrapper for hashlib's digest operations that hashes a piece of data
    repeatedly if needed."""
    dig = getattr(hashlib, _alg)
    for _ in range(it):
        msg = dig(bytes(str(msg), "utf-8")).hexdigest()
    return msg


def b1_average(w: int, f: str, it: int, msglen: int):
    """Average value of many sequences of `T1` blocks."""
    assert f in hashlib.algorithms_guaranteed

    m = hashlib.new(f).digest_size << 3
    msgs = urandom(msglen * it)

    for i in range(it):
        msg = msgs[msglen * i : msglen * (i + 1)]
        print(sum(b1(f, msg, m, w)) / t1(m, w))


def wm_comb(w: int):
    """Table showing unused bits on the checksum for various combinations of
    `m` and `W`."""
    sec_params = [128, 192, 256, 512]
    for _w in range(2, w + 1):
        print("\nw = {:2d} |  m  | nc | nu | t2*w".format(_w))
        for m in sec_params:
            print(
                "       | {} | {:2d} | {:2d} | {:3d}".format(
                    m, nc(m, _w), nu(m, _w), t2(m, _w) * _w
                )
            )


def choose_h(msg: str, _R: str) -> str:
    """Optimization that pre-processes the message hash to choose one with
    higher values on the `T1` blocks."""
    r, val = 0, 0
    for v in range(int(_R)):
        _h = bin(int(chash(alg, msg + str(v), 1), 16))[2:].zfill(n)
        exp = [_h[i : i + W] for i in range(0, T1 * W, W)]
        mean = sum(map(lambda x: int(x, 2), exp)) / len(exp)
        if mean > val:
            r = v
            val = mean

    return bin(int(chash(alg, msg + str(r), 1), 16))[2:].zfill(n)


def getexp(_h: str, pad: bool = False) -> Tuple[List[int]]:
    """Divides the message's hash in `T1` blocks of base-`W` numbers, with an
    additional `T2` blocks of checksum. Optionally turns all unused checksum
    bits to 1."""
    hmpad = [_h[i : i + W] for i in range(0, T1 * W, W)]
    csum = sum(map(lambda x: (2 ** W - 1) - int(x, 2), hmpad))
    cpad = str(bin(csum)).replace(
        "0b", int(T2 * W - log2(csum)) * str(int(pad))
    )
    tcpad = [cpad[i : i + W] for i in range(0, T2 * W, W)]
    exp = list(map(lambda x: int(x, 2), hmpad + tcpad))
    return exp, [(2 ** W - 1) - i for i in exp]


if __name__ == "__main__":
    # b1_average(16, 'sha256', 2**16, 32)
    # wm_comb(16)
    algs = hashlib.algorithms_guaranteed
    assert len(argv) == 5, "Usage: {} W alg R msg".format(argv[0])
    _, W, alg, R, message = argv

    W = int(W)
    n = hashlib.new(alg).digest_size * 8
    T1 = ceil(n / W)
    T2 = ceil((floor(log2(T1)) + 1 + W) / W)
    T = T1 + T2

    # std, -b, -r, -br
    for h in [
        bin(int(chash(alg, message, 1), 16))[2:].zfill(n),
        choose_h(message, R),
    ]:
        exp_s, exp_v = getexp(h)
        # sig B1, sig B2, sig B, ver B1, ver B2, ver B
        print(
            sum(exp_s[:T1]),
            sum(exp_s[T1:]),
            sum(exp_s),
            sum(exp_v[:T1]),
            sum(exp_v[T1:]),
            sum(exp_v),
            end="    ",
        )
    print()
