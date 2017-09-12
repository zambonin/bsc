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


algorithms = ["sha256_", "blake2s_", "sha3_256_"]
modes = ["noop", "small", "sumavg", "avg", "half"]
files = ["".join(i) + ".out" for i in product(algorithms, modes)]

means = [avg_data(i) for i in files]
noop_ver    = [means[0][1], means[5][1], means[10][1]]
noop_sign   = [means[0][0], means[5][0], means[10][0]]
small_ver   = [means[1][1], means[6][1], means[11][1]]
small_sign  = [means[1][0], means[6][0], means[11][0]]
sumavg_ver  = [means[2][1], means[7][1], means[12][1]]
sumavg_sign = [means[2][0], means[7][0], means[12][0]]
avg_ver     = [means[3][1], means[8][1], means[13][1]]
avg_sign    = [means[3][0], means[8][0], means[13][0]]
half_ver    = [means[4][1], means[9][1], means[14][1]]
half_sign   = [means[4][0], means[9][0], means[14][0]]

bar_pos = np.arange(len(noop_ver))
width = 0.17

plt.bar(bar_pos + 0 * width, noop_sign, width, alpha=0.3, label='noop-S', color='red')
plt.bar(bar_pos + 0 * width, noop_ver, width, bottom=noop_sign, alpha=0.3, label='noop-V', color='blue')
plt.bar(bar_pos + 1 * width, small_sign, width, alpha=0.4, label='small-S', color='red')
plt.bar(bar_pos + 1 * width, small_ver, width, bottom=small_sign, alpha=0.4, label='small-V', color='blue')
plt.bar(bar_pos + 2 * width, sumavg_sign, width, alpha=0.5, label='sumavg-S', color='red')
plt.bar(bar_pos + 2 * width, sumavg_ver, width, bottom=sumavg_sign, alpha=0.5, label='sumavg-V', color='blue')
plt.bar(bar_pos + 3 * width, avg_sign, width, alpha=0.6, label='avg-V', color='red')
plt.bar(bar_pos + 3 * width, avg_ver, width, bottom=avg_sign, label='avg-S', alpha=0.6, color='blue')
plt.bar(bar_pos + 4 * width, half_sign, width, alpha=0.7, label='half-V', color='red')
plt.bar(bar_pos + 4 * width, half_ver, width, bottom=half_sign, label='half-S', alpha=0.7, color='blue')

plt.legend(loc=4)
plt.tight_layout()
plt.xticks(bar_pos + width, algorithms)
plt.show()
