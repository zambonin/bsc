#!/bin/bash
#
# Usage: $0 <no. of iterations>
#
# Generates LaTeX output for average values of T1 and T2 blocks needed to
# verify various random Winternitz signatures. Takes in account optimizations
# implemented in the `wint_exp.py` Python script.
#
# If one wants to generate this data for values needed to generate signatures,
# remember to edit `wint_exp.py` like this:
#  * inside the `choose_h` function, change `val` from 0 to 1 << 32 or some
#    large value; also remember to invert the conditional a
#  * delete Wots-b and Wots-br lines from this script, since signature
#    generation does not benefit from higher checksum values;
#  * fix AWK columns (subtract 3 from each value).

for w in 4 8 16 ; do
  printf "\\multirow{8}{*}{%d} " "$w"
  for R in 1 25 200 3500 ; do
  printf "& \\multirow{2}{*}{%d}\n" "$R"
    parallel -n1 python "wint_exp.py" $w sha256 $R :::                        \
      "$(head -c 1024 /dev/urandom | xxd -p | paste -sd '')"                  \
      "$(seq 1 "${1:-8}")"                                                    \
      | awk '{
          b1_s += $4;    b2_s += $5;   b_s += $6;
          b1_b += $10;   b2_b += $11;  b_b += $12;
          b1_r += $16;   b2_r += $17;  b_r += $18;
          b1_br += $22;  b2_br += $23; b_br += $24
        } END {
          printf("   & %16s & %10.2f & %10.2f & %10.2f \\\\\n",
            "\\textsc{Wots}", b1_s / NR, b2_s / NR, b_s / NR);
          printf(" & & %16s & %10.2f & %10.2f & %10.2f \\\\\n",
            "\\textsc{Wots-b}", b1_b / NR, b2_b / NR, b_b / NR);
          printf(" & & %16s & %10.2f & %10.2f & %10.2f \\\\\n",
            "\\textsc{Wots-r}", b1_r / NR, b2_r / NR, b_r / NR);
          printf(" & & %16s & %10.2f & %10.2f & %10.2f \\\\\n",
            "\\textsc{Wots-br}", b1_br / NR, b2_br / NR, b_br / NR);
        }'
  done
done
