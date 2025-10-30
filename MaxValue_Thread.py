import argparse
import threading
import random
import time
import os

try:
    import psutil
except ImportError:
    psutil = None

def measure_memory():
    #Return current process RSS in bytes
    if psutil:
        p = psutil.Process(os.getpid())
        return p.memory_info().rss
    return 0

def worker_local_max(data_slice, shared_buf, lock=None):
    #Compute local max and update shared buffer if larger
    local_max = max(data_slice) if data_slice else -10**9

    # Synchronized update if lock provided
    if lock:
        with lock:
            if local_max > shared_buf['val']:
                shared_buf['val'] = local_max
    else:
        # Non-atomic update (race condition)
        if local_max > shared_buf['val']:
            shared_buf['val'] = local_max

def run_max_value(size: int, workers: int, use_lock: bool):
    # Generate random data
    data = [random.randint(0, 10**7) for _ in range(size)]
    chunk_size = (size + workers - 1) // workers

    # Shared buffer (single integer)
    shared_buf = {'val': -10**9}
    lock = threading.Lock() if use_lock else None

    mem_before = measure_memory()
    t0 = time.perf_counter()

    # Map phase: start threads
    threads = []
    for i in range(workers):
        start = i * chunk_size
        end = min(start + chunk_size, size)
        slice_copy = data[start:end]
        th = threading.Thread(target=worker_local_max,
                              args=(slice_copy, shared_buf, lock))
        th.start()
        threads.append(th)

    # Wait for all threads to finish
    map_end = time.perf_counter()
    for th in threads:
        th.join()

    # Reduce phase: single read of shared buffer
    global_max = shared_buf['val']
    reduce_end = time.perf_counter()
    mem_after = measure_memory()

    # Correctness check
    correct = global_max == max(data)

    # Print stats of its correctness
    print(f"Max-Value Aggregation: size={size} workers={workers} sync={use_lock}")
    print(f"Map phase time: {map_end - t0:.6f} s")
    print(f"Reduce phase time: {reduce_end - map_end:.6f} s")
    print(f"Total time: {reduce_end - t0:.6f} s")
    if psutil:
        print(f"Parent memory (RSS) before: {mem_before} bytes after: {mem_after} bytes")
        print("Note: threads share memory; only parent RSS measured.")
    else:
        print("Memory measurement skipped (psutil not installed).")
    print(f"Reported global max: {global_max} (Correct: {correct})")
    if not correct:
        print("ERROR: global max is incorrect due to race conditions!")
    print()

def main():
    # Choose the number of workers and size you want
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4, help="Number of mapper threads")
    parser.add_argument("--size", type=int, default=131072, help="Total input size")
    parser.add_argument("--sync", dest="sync", action="store_true", help="Use synchronization (Lock)")
    parser.add_argument("--nosync", dest="sync", action="store_false", help="Do not use synchronization")
    parser.set_defaults(sync=True)
    args = parser.parse_args()

    run_max_value(args.size, args.workers, args.sync)

if __name__ == "__main__":
    main()
