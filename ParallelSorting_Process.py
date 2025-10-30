import argparse
import random
import time
import heapq
import os
from multiprocessing import Process, Queue

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

def worker_sort(data_slice, queue, index):
    #Sort a slice and put it in the queue along with its index
    sorted_slice = sorted(data_slice)
    queue.put((index, sorted_slice))

def run_process_sort(size: int, workers: int):
    # Generate random data
    data = [random.randint(0, 10**7) for _ in range(size)]
    chunk_size = (size + workers - 1) // workers

    # Memory before
    mem_before = measure_memory()
    t0 = time.perf_counter()

    # Map phase: start processes
    queue = Queue()
    processes = []
    for i in range(workers):
        start = i * chunk_size
        end = min(start + chunk_size, size)
        slice_copy = data[start:end]
        p = Process(target=worker_sort, args=(slice_copy, queue, i))
        p.start()
        processes.append(p)

    # Collect sorted chunks
    sorted_chunks = [None] * workers
    map_end = time.perf_counter()
    for _ in range(workers):
        idx, sorted_slice = queue.get()
        sorted_chunks[idx] = sorted_slice

    # Wait for all processes to finish
    for p in processes:
        p.join()

    # Reduce phase: merge all sorted chunks
    final_sorted = list(heapq.merge(*sorted_chunks))
    end = time.perf_counter()
    mem_after = measure_memory()

    # Correctness check
    correct = final_sorted == sorted(data)

    # Print stats of its correctness
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
    #Choose the number of workers and size you want
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4, help="Number of mapper processes")
    parser.add_argument("--size", type=int, default=131072, help="Total input size")
    args = parser.parse_args()
    run_process_sort(args.size, args.workers)

if __name__ == "__main__":
    main()

