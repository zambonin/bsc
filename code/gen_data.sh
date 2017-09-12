#!/bin/bash
# usage: $0 <no. of iterations>

for s in noop small sumavg avg half ; do
  for h in sha256 sha3_256 blake2s ; do
    echo $h $s
    parallel -n1 python "winternitz-$s.py" $h ::: $(head -c 2048 /dev/urandom \
      | xxd -ps | paste -sd '') "$(seq 1 ${1:-8})" >| "${h}_${s}.out"
  done
done
