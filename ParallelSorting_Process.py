#!/usr/bin/env python3
"""
Part 1: Parallel Sorting (process-based version)

- Splits the array into `workers` chunks.
- Each mapper process sorts its chunk and puts (idx, sorted_list) onto a multiprocessing.Queue.
- Reducer (main process) collects sorted chunks and merges them using heapq.merge.

Usage:
  python3 part1_process.py --workers 4 --size 131072
"""
from typing import List
import argparse
import random
import time
import multiprocessing as mp
import heapq
import os

try:
    import psutil
except Exception:
    psutil = None

def measure_memory():
    if psutil:
        p = psutil.Process(os.getpid())
        return p.memory_info().rss
    else:
        return 0

def proc_worker_sort(arr_slice: List[int], out_q: mp.Queue, idx: int):
    arr_slice.sort()
    out_q.put((idx, arr_slice))

def run_process_sort(size: int, workers: int):
    data = [random.randint(0, 10**7) for _ in range(size)]
    chunk_size = (size + workers - 1) // workers

    q: mp.Queue = mp.Queue()
    processes = []

    mem_before = measure_memory()
    t0 = time.perf_counter()

    # Start mapper processes
    for i in range(workers):
        start = i * chunk_size
        end = min(start + chunk_size, size)
        slice_copy = data[start:end]
        p = mp.Process(target=proc_worker_sort, args=(slice_copy, q, i))
        p.start()
        processes.append(p)

    # Wait for map phase to finish
    for p in processes:
        p.join()
    map_end = time.perf_counter()

    # Collect sorted chunks
    chunks = [None] * workers
    for _ in range(workers):
        idx, sorted_chunk = q.get()
        chunks[idx] = sorted_chunk

    # Reduce: merge
    merged = list(heapq.merge(*[c for c in chunks if c]))
    end = time.perf_counter()
    mem_after = measure_memory()

    correct = merged == sorted(data)

    print(f"Process sort: size={size} workers={workers}")
    print(f"Map phase time: {map_end - t0:.6f} s")
    print(f"Reduce (merge) time: {end - map_end:.6f} s")
    print(f"Total time: {end - t0:.6f} s")
    if psutil:
        print(f"Parent memory (RSS) before: {mem_before} bytes after: {mem_after} bytes")
        print("Note: child processes memory is not included in parent RSS.")
    else:
        print("Memory measurement skipped (psutil not installed).")
    print(f"Correct: {correct}")
    if not correct:
        print("ERROR: result not sorted properly!")
    print()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4, help="Number of mapper workers")
    parser.add_argument("--size", type=int, default=131072, help="Total input size")
    args = parser.parse_args()
    run_process_sort(args.size, args.workers)

if __name__ == "__main__":
    main()
