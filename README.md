# MapReduce-style Parallel Sorting and Max Aggregation (Single-host)

This repository contains an instructional implementation of two MapReduce-style tasks, implemented both with multithreading and multiprocessing on a single host:

- Part 1 — Parallel Sorting (MapReduce style)
  - Threaded implementation: `part1_thread.py`
  - Process-based implementation: `part1_process.py`
- Part 2 — Max-Value Aggregation with constrained shared memory (one-integer buffer)
  - Threaded implementation: `part2_thread.py`
  - Process-based implementation: `part2_process.py`

Goals:
- Practice process and thread creation and management
- Practice IPC (queues/shared memory) and synchronization (locks)
- Measure execution time and memory usage with different worker counts (1, 2, 4, 8)
- Demonstrate correctness for small inputs and performance for larger inputs

Requirements
- Python 3.8+
- Optional: `psutil` for more accurate memory measurements (pip install psutil)

Quick usage
- Run Part 1 (sorting) with threads:
  python3 part1_thread.py --workers 4 --size 131072
- Run Part 1 (sorting) with processes:
  python3 part1_process.py --workers 4 --size 131072
- Run Part 2 (max) with threads (synchronized):
  python3 part2_thread.py --workers 8 --size 131072 --sync
- Run Part 2 (max) with processes (unsynchronized — shows race conditions):
  python3 part2_process.py --workers 8 --size 131072 --nosync

Each script prints:
- timing for map phase (sorting/local max)
- time for reduce phase (merge / read final value)
- memory usage (approx.) for the parent process
- correctness checks (compares to Python built-ins)

See `report.md` for a minimal project report with diagrams, implementation notes, and sample results.
