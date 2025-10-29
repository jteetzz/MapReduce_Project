#!/usr/bin/env python3
"""
Part 2: Max-Value Aggregation with constrained shared memory (threaded)

- Shared buffer: one integer (global max stored in a Python int wrapped in a dict for mutability)
- Each mapper thread computes local max and tries to update the shared buffer.
- --sync uses a threading.Lock to protect read-compare-write.
- --nosync attempts updates without locks to demonstrate race conditions.

Usage:
  python3 part2_thread.py --workers 4 --size 131072 --sync
"""
import argparse
import random
import time
import threading
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

def worker_local_max_thread(data_slice, shared_buf, lock, sync: bool):
    local_max = max(data_slice) if data_slice else -10**9
    # Attempt to update shared buffer (single integer)
    if sync:
        with lock:
            if local_max > shared_buf['val']:
                shared_buf['val'] = local_max
    else:
        # Non-atomic read/compare/write (race-prone)
        if local_max > shared_buf['val']:
            shared_buf['val'] = local_max

def run_threaded_max(size: int, workers: int, sync: bool):
    data = [random.randint(0, 10**7) for _ in range(size)]
    chunk_size = (size + workers - 1) // workers

    shared_buf = {'val': -10**9}  # "constrained" single integer slot
    lock = threading.Lock()

    t0 = time.perf_counter()
    mem_before = measure_memory()

    threads = []
    for i in range(workers):
        start = i * chunk_size
        end = min(start + chunk_size, size)
        slice_copy = data[start:end]
        th = threading.Thread(target=worker_local_max_thread,
                              args=(slice_copy, shared_buf, lock, sync))
        th.start()
        threads.append(th)

    for th in threads:
        th.join()

    t1 = time.perf_counter()
    mem_after = measure_memory()

    correct = shared_buf['val'] == max(data) if data else True

    print(f"Threaded max: size={size} workers={workers} sync={sync}")
    print(f"Time (map+reduce): {t1 - t0:.6f} s")
    if psutil:
        print(f"Memory (RSS) before: {mem_before} bytes after: {mem_after} bytes")
    else:
        print("Memory measurement skipped (psutil not installed).")
    print(f"Reported global max: {shared_buf['val']} (correct: {correct}, expected: {max(data) if data else None})")
    print()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4, help="Number of mapper workers")
    parser.add_argument("--size", type=int, default=131072, help="Total input size")
    parser.add_argument("--sync", dest="sync", action="store_true", help="Use synchronization (Lock)")
    parser.add_argument("--nosync", dest="sync", action="store_false", help="Do not use synchronization")
    parser.set_defaults(sync=True)
    args = parser.parse_args()
    run_threaded_max(args.size, args.workers, args.sync)

if __name__ == "__main__":
    main()
