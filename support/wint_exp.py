#!/usr/bin/env python

import hashlib
from math import ceil, floor, log2
from os import urandom
from typing import List, Tuple
from sys import argv


def t1(m: int, w: int) -> int:
    return ceil(m / w)


def t2(m: int, w: int) -> int:
    return ceil((floor(log2(t1(m, w))) + 1 + w) / w)


def nc(m: int, w: int) -> int:
    return ceil(log2(t1(m, w) * 2**w - 1))


def nu(m: int, w: int) -> int:
    return t2(m, w) * w - nc(m, w)


def b1(alg: str, msg: str, m: int, w: int) -> List[int]:
    digest = bin(int(chash(alg, msg, 1), 16))[2:].zfill(m)
    split = [digest[j:j+w] for j in range(0, t1(m, w) * w, w)]
    return list(map(lambda x: int(x, 2), split))


def b2(exp: List[int], m: int, w: int, pad: bool=False) -> List[int]:
    csum = sum(map(lambda x: (2**w - 1) - x, exp))
    flip = int(t2(m, w) * w - log2(csum)) * str(int(pad))
    cpad = str(bin(csum)).replace('0b', flip)
    tcpad = [cpad[i:i+w] for i in range(0, t2(m, w) * w, w)]
    return list(map(lambda x: int(x, 2), tcpad))


def chash(alg: str, msg: str, it: int) -> str:
    dig = getattr(hashlib, alg)
    for _ in range(it):
        msg = dig(bytes(str(msg), 'utf-8')).hexdigest()
    return msg


def b1_average(w: int, f: str, it: int, msglen: int):
    algs = hashlib.algorithms_guaranteed
    assert f in algs

    m = hashlib.new(f).digest_size << 3
    msgs = urandom(msglen * it)

    for i in range(it):
        msg = msgs[msglen*i:msglen*(i+1)]
        print(sum(b1(f, msg, m, w)) / t1(m, w))


def wm_comb(w: int):
    sec_params = [128, 192, 256, 512]
    w_values = range(2, w + 1)

    for w in w_values:
        print("\nw = {:2d} |  m  | nc | nu | t2*w".format(w))
        for m in sec_params:
            print("       | {} | {:2d} | {:2d} | {:3d}".format(
                m, nc(m, w), nu(m, w), t2(m, w) * w))


def choose_h(msg: str, R: str) -> str:
    r, val = 0, 0
    for v in range(int(R)):
        h = bin(int(chash(alg, msg + str(v), 1), 16))[2:].zfill(n)
        exp = [h[i:i+W] for i in range(0, T1 * W, W)]
        mean = sum(map(lambda x: int(x, 2), exp)) / len(exp)
        if mean > val:
            r = v
            val = mean

    return bin(int(chash(alg, msg + str(r), 1), 16))[2:].zfill(n)


def getexp(alg: str, h: str, pad: bool=False) -> Tuple[List[int]]:
    hmpad = [h[i:i+W] for i in range(0, T1 * W, W)]
    csum = sum(map(lambda x: (2**W - 1) - int(x, 2), hmpad))
    cpad = str(bin(csum)).replace('0b', int(T2 * W - log2(csum)) * str(int(pad)))
    tcpad = [cpad[i:i+W] for i in range(0, T2 * W, W)]
    exp = list(map(lambda x: int(x, 2), hmpad + tcpad))
    return exp, [(2**W - 1) - i for i in exp]


if __name__ == '__main__':
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
    for h in [bin(int(chash(alg, message, 1), 16))[2:].zfill(n),
              choose_h(message, R)]:
        exp_s, exp_v = getexp(alg, h)
        # sig B1, sig B2, sig B, ver B1, ver B2, ver B
        print(sum(exp_s[:T1]), sum(exp_s[T1:]), sum(exp_s),
                sum(exp_v[:T1]), sum(exp_v[T1:]), sum(exp_v), end='    ')
    print()
