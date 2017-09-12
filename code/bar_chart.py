import numpy as np
import matplotlib.pyplot as plt
from itertools import product


def avg_data(path):
    with open(path, 'r') as f:
        avg = lambda x: sum(x) // len(x)
        h_qnt = [i.split()[2:] for i in f.readlines()]
        s_qnt = [int(i[0]) for i in h_qnt]
        v_qnt = [int(i[1]) for i in h_qnt]
        return avg(s_qnt), avg(v_qnt)


files = ["".join(i) + ".out" for i in product(
    ["sha256_", "blake2s_", "sha3_256_"], ["noop", "small", "sumavg"])]

width = 0.2
op = 0.8

means = [avg_data(i) for i in files]
sha256_upper = [means[0][1], means[3][1], means[6][1]]
sha256_lower = [means[0][0], means[3][0], means[6][0]]
blake2s_upper = [means[1][1], means[4][1], means[7][1]]
blake2s_lower = [means[1][0], means[4][0], means[7][0]]
sha3256_upper = [means[2][1], means[5][1], means[8][1]]
sha3256_lower = [means[2][0], means[5][0], means[8][0]]

bar_pos = np.arange(len(sha256_upper))

plt.bar(bar_pos + 0 * width, sha256_lower, width, alpha=op)
plt.bar(bar_pos + 0 * width, sha256_upper, width, bottom=sha256_lower, alpha=op)
plt.bar(bar_pos + 1 * width, blake2s_lower, width, alpha=op)
plt.bar(bar_pos + 1 * width, blake2s_upper, width, bottom=blake2s_lower, alpha=op)
plt.bar(bar_pos + 2 * width, sha3256_lower, width, alpha=op)
plt.bar(bar_pos + 2 * width, sha3256_upper, width, bottom=sha3256_lower, alpha=op)

plt.xticks(bar_pos + width, ["sha256", "blake2s", "sha3256"])
plt.show()
