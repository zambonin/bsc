#!/usr/bin/env python

import hashlib
from math import ceil, floor, log2
from sys import argv
from itertools import product
from os import urandom

def chash(alg, msg, it):
    dig = getattr(hashlib, alg)
    for _ in range(it):
        msg = dig(bytes(str(msg), 'utf-8')).hexdigest()
    return msg


def smalldiff(s):
    m = 2**W - 1 - max(s)
    return [i + m for i in s]


def applytable(s):
    t = sorted([1024 * (i + 1) for i in range(len(s))], reverse=True)
    while t:
        n = t.pop()
        e = s[s.index(min(s))]
        if n + e > 2**W - 1:
            break
        s[s.index(min(s))] += n
    return s


def standard(s=False):
    hmpad = [H[i:i+W] for i in range(0, T1 * W, W)]
    csum = sum(map(lambda x: (2**W - 1) - int(x, 2), hmpad))
    cpad = str(bin(csum)).replace('0b', int(T2 * W - log2(csum)) * '0')
    tcpad = [cpad[i:i+W] for i in range(0, T2 * W, W)]
    final = list(map(lambda x: int(x, 2), hmpad + tcpad))
    return smalldiff(final) if s else final


def sumhalf(s):
    n = [i + ((i < 2**(W-1)) * (2**(W - 1))) for i in standard()]
    return smalldiff(n) if s else n


def sumavg(s):
    f = standard()
    avg = sum(f) // len(f)
    n = [2**W - 1 - abs(i - avg) for i in f]
    return smalldiff(n) if s else n


def halfdiff(s):
    n = [2**W - 1 - abs(i - (2**(W - 1))) for i in standard()]
    return smalldiff(n) if s else n


def verpercent(n):
    m = T * (2**W - 1)
    return (m - sum(n)) / m


if __name__ == '__main__':
    algs = hashlib.algorithms_guaranteed
    assert len(argv) == 3 and argv[2] in algs

    repeat = int(argv[1])
    alg = argv[2]

    W = 16
    n = hashlib.new(alg).digest_size * 8
    T1 = ceil(n / W)
    T2 = ceil((floor(log2(T1)) + 1 + W) / W)
    T = T1 + T2

    opts = list(product([standard, sumhalf, sumavg, halfdiff],
            [lambda x: x, applytable]))

    percents = [0 for _ in range(len(opts))]
    msglen = 2048
    msgs = urandom(msglen * repeat)

    for k in range(repeat):
        message = msgs[msglen*k:msglen*(k+1)]
        H = bin(int(chash(alg, message, 1), 16))[2:].zfill(n)
        for i, f in enumerate(opts):
            percents[i] += verpercent(f[1](f[0](True)))

    for f, i in sorted(zip(opts, percents), key=lambda x: x[1]):
        print("{:<8} + {:<10} - {}%".format(
            f[0].__name__, f[1].__name__, i / repeat))
