#!/usr/bin/env bash
# Simple helper: runs a set of experiments for both parts
# Usage: ./run_experiments.sh

PY=python3

SIZES=(32 131072)
WORKERS=(1 2 4 8)

echo "=== PART 1: Sorting (threads) ==="
for size in "${SIZES[@]}"; do
  for w in "${WORKERS[@]}"; do
    echo "Size=$size Workers=$w"
    $PY part1_thread.py --size $size --workers $w
  done
done

echo "=== PART 1: Sorting (processes) ==="
for size in "${SIZES[@]}"; do
  for w in "${WORKERS[@]}"; do
    echo "Size=$size Workers=$w"
    $PY part1_process.py --size $size --workers $w
  done
done

echo "=== PART 2: Max (threads, sync/nosync) ==="
for size in "${SIZES[@]}"; do
  for w in "${WORKERS[@]}"; do
    echo "Size=$size Workers=$w SYNC"
    $PY part2_thread.py --size $size --workers $w --sync
    echo "Size=$size Workers=$w NOSYNC"
    $PY part2_thread.py --size $size --workers $w --nosync
  done
done

echo "=== PART 2: Max (processes, sync/nosync) ==="
for size in "${SIZES[@]}"; do
  for w in "${WORKERS[@]}"; do
    echo "Size=$size Workers=$w SYNC"
    $PY part2_process.py --size $size --workers $w --sync
    echo "Size=$size Workers=$w NOSYNC"
    $PY part2_process.py --size $size --workers $w --nosync
  done
done
