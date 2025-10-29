```text
Project Report: MapReduce-style Parallel Sorting and Max-Value Aggregation
Author: (Student)
Date: (Fill date)

1. Project Description
- Implemented two MapReduce-style tasks on a single host:
  * Part 1: Parallel Sorting — map phase sorts chunks; reduce phase merges sorted chunks.
  * Part 2: Max aggregation with constrained shared memory — workers update a single-integer shared buffer with synchronization.

- Implementations provided for both multithreading (threads) and multiprocessing (processes).

Why multithreading and multiprocessing?
- Multithreading: lightweight threads that share address space — suitable for teaching synchronization (locks) and shared memory.
- Multiprocessing: independent processes with their own memory — suitable for teaching explicit IPC (queues, shared Value) and how OS isolates memory.

2. How to run
Prereqs:
- Python 3.8+
- Optional: pip install psutil

Examples:
- Sorting (threads): python3 part1_thread.py --workers 4 --size 131072
- Sorting (processes): python3 part1_process.py --workers 4 --size 131072
- Max (threads, sync): python3 part2_thread.py --workers 4 --size 131072 --sync
- Max (processes, no sync): python3 part2_process.py --workers 4 --size 131072 --nosync

3. Code structure & Diagrams
Files:
- part1_thread.py: threaded sorting
- part1_process.py: process-based sorting
- part2_thread.py: threaded max aggregation
- part2_process.py: process-based max aggregation
- README.md, report.md

Diagrams (ASCII):

Part 1 (threaded)
Main thread:
  - generates data -> splits -> spawns mapper threads -> each thread sorts local chunk -> pushes sorted chunk to queue
  - after join: collects k sorted chunks -> reducer merges (heapq.merge) -> final sorted array

Part 1 (process)
Main process:
  - generates data -> splits -> spawn mapper processes -> each process sorts local chunk -> put (idx, sorted_chunk) on mp.Queue
  - after join: collect chunks from queue -> reducer merges -> final sorted array

Part 2 (shared memory)
Threaded:
  - shared buffer (single integer) stored in shared Python object (dict)
  - workers compute local max and attempt to update shared buffer with or without lock

Process:
  - shared buffer: multiprocessing.Value (one integer)
  - workers compute local max and attempt to update shared Value with or without Lock

4. Implementation details
Tools / libraries:
- Python standard library: threading, multiprocessing, heapq, argparse, time, random
- psutil (optional) for memory measurement

Process management:
- Threaded versions use threading.Thread
- Process versions use multiprocessing.Process

IPC:
- For sorted-chunks: multiprocessing.Queue used to send sorted lists from mappers to reducer
- For shared single-integer buffer: multiprocessing.Value used to simulate constrained shared memory

Threading:
- Manual thread creation (one thread per mapper) for simplicity
- Threads share memory — locking via threading.Lock for synchronization

Synchronization strategy:
- For max-aggregation: read-compare-write protected using Lock when --sync is passed
- For the unsynchronized variant, no lock is used to demonstrate possible race conditions

Performance measurement:
- Timings via time.perf_counter() for map and reduce phases
- Memory: optional psutil.Process(...).memory_info().rss snapshot before and after (parent process only)
  Note: Parent RSS does not include child process memory on many OSes. For process-level full memory accounting, tools like ps or pmap per-PID are needed.

5. Performance evaluation (minimal)
- Correctness tests:
  * For size=32: both sorting versions compare merged result to sorted(original) to assert correctness.
  * For max aggregation: compare shared buffer value to max(original).

- Timing tests:
  * Run same script with workers = 1,2,4,8 and record times printed.

Sample observations (expected):
- Sorting:
  * Threaded version may not speed up much in CPython when sorting CPU-bound workloads because of GIL; but using Python's built-in sort releases the GIL in C, so some parallelism can occur for list.sort on slices. Process version often scales better for CPU-bound sorts as processes bypass the GIL.
  * Merge (reduce) time increases with number of chunks but is usually small compared to map sorting time.

- Max aggregation:
  * With proper synchronization, correctness is guaranteed.
  * Unsynchronized runs (esp. with processes) can produce wrong results due to race conditions.
  * Overhead of locking is usually small relative to the compute in each mapper, unless chunks are extremely small.

6. Conclusion
- The project demonstrates core OS concepts: parallelism, IPC, and synchronization.
- Processes provide stronger isolation and often better CPU parallelism for CPU-bound tasks in CPython.
- Threads are useful to teach locking and shared-state access but can be limited by the GIL for CPU-bound workloads.
- Shared-memory constraints (single-integer buffer) force careful synchronization for correctness.

Limitations & Improvements:
- Memory totals of child processes are not included in parent RSS measurement — for full-system memory measures, collect per-PID measurements.
- For very large datasets, passing whole sorted slices via Queue causes pickling overhead; using shared memory segments or memory-mapped files would reduce copy overhead.
- A more faithful MapReduce implementation could use intermediate file storage and streaming merges for very large data sizes.

End of report.
