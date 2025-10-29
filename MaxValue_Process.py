#!/usr/bin/env python3
"""
Part 2: Max-Value Aggregation with constrained shared memory (process-based)

- Shared buffer: one multiprocessing.Value ('i' or 'l') used to hold the current global max.
- Each mapper process computes local max and tries to update the shared buffer.
- --sync uses a multiprocessing.Lock around the read-compare-write.
- --nosync attempts updates without locks in order to demonstrate race conditions.

Usage:
  python3 part2_process.py --workers 4 --size 131072 --sync
"""
import argparse
import random
import time
import multiprocessing as mp
import os
import ctypes

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

def proc_worker_local_max(data_slice, shared_val, lock, sync: bool):
    local_max = max(data_slice) if data_slice else -10**9
    if sync:
        with lock:
            if local_max > shared_val.value:
                shared_val.value = local_max
    else:
        # Read/compare/write without lock — race-prone
        if local_max > shared_val.value:
            shared_val.value = local_max

def run_process_max(size: int, workers: int, sync: bool):
    data = [random.randint(0, 10**7) for _ in range(size)]
    chunk_size = (size + workers - 1) // workers

    # Use 'l' (signed long) — platform-dependent; safe for typical int ranges
    shared_val = mp.Value(ctypes.c_long, -10**9)
    lock = mp.Lock()

    processes = []
    t0 = time.perf_counter()
    mem_before = measure_memory()

    for i in range(workers):
        start = i * chunk_size
        end = min(start + chunk_size, size)
        slice_copy = data[start:end]
        p = mp.Process(target=proc_worker_local_max, args=(slice_copy, shared_val, lock, sync))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    t1 = time.perf_counter()
    mem_after = measure_memory()

    correct = shared_val.value == max(data) if data else True

    print(f"Process max: size={size} workers={workers} sync={sync}")
    print(f"Time (map+reduce): {t1 - t0:.6f} s")
    if psutil:
        print(f"Parent RSS before: {mem_before} bytes after: {mem_after} bytes")
        print("Note: child processes memory not included in parent's RSS")
    else:
        print("Memory measurement skipped (psutil not installed).")
    print(f"Reported global max: {shared_val.value} (correct: {correct}, expected: {max(data) if data else None})")
    print()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4, help="Number of mapper workers")
    parser.add_argument("--size", type=int, default=131072, help="Total input size")
    parser.add_argument("--sync", dest="sync", action="store_true", help="Use synchronization (Lock)")
    parser.add_argument("--nosync", dest="sync", action="store_false", help="Do not use synchronization")
    parser.set_defaults(sync=True)
    args = parser.parse_args()
    run_process_max(args.size, args.workers, args.sync)

if __name__ == "__main__":
    main()
