import hashlib
from math import ceil, floor, log2
from random import getrandbits
from sys import argv


def chash(alg, msg, it):
    dig = getattr(hashlib, alg)
    for _ in range(it):
        msg = dig(bytes(str(msg), 'utf-8')).hexdigest()
    return msg


def choose_h(msg, R):
    r, val = 0, 0
    for v in range(int(R)):
        h = bin(int(chash(alg, message + str(v), 1), 16))[2:].zfill(n)
        exp = [h[i:i+W] for i in range(0, T1 * W, W)]
        mean = sum(map(lambda x: int(x, 2), exp)) / len(exp)
        if mean > val:
            r = v
            val = mean

    return bin(int(chash(alg, message + str(r), 1), 16))[2:].zfill(n)


def getexp(alg, h, pad=False):
    hmpad = [h[i:i+W] for i in range(0, T1 * W, W)]
    csum = sum(map(lambda x: (2**W - 1) - int(x, 2), hmpad))
    cpad = str(bin(csum)).replace('0b', int(T2 * W - log2(csum)) * str(int(pad)))
    tcpad = [cpad[i:i+W] for i in range(0, T2 * W, W)]
    exp = list(map(lambda x: int(x, 2), hmpad + tcpad))
    return exp, [(2**W - 1) - i for i in exp]


if __name__ == '__main__':
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
        for p in [False, True]:
            exp_s, exp_v = getexp(alg, h, pad=p)
            # sig B1, sig B2, sig B, ver B1, ver B2, ver B
            print(sum(exp_s[:T1]), sum(exp_s[T1:]), sum(exp_s),
                    sum(exp_v[:T1]), sum(exp_v[T1:]), sum(exp_v), end='    ')
    print()
