# MapReduce Systems for Parallel Sorting and Max-Value Aggregation with Constrained Memory

## Overview
This project implements **two MapReduce-style tasks** designed to explore **parallelism**, **inter-process communication (IPC)**, and **synchronization** in operating systems.  
I used both **multithreading** and **multiprocessing** to simulate the MapReduce model on a single machine.

The project is divided into:
1. **Parallel Sorting (MapReduce Style)**
2. **Max-Value Aggregation with Constrained Shared Memory**

---

## MapReduce
**MapReduce** is a programming model that allows large-scale data processing across distributed clusters by splitting work into two main stages:

- **Map** – Each worker processes a portion of the input data and emits intermediate results.  
- **Reduce** – The intermediate results are aggregated into final output.

This project **simulates MapReduce locally** (not distributed) using:
- Multithreading or multiprocessing for worker execution.
- Shared memory or message passing for communication.

---

## Project Structure
```
MapReduce_Project/
│
├── ParallelSorting_Thread.py     # Multithreaded MapReduce-style sorting
├── MaxValue_Thread.py            # Thread-based max-value aggregation
├── ParallelSorting_Process.py           # Process-based max-value aggregation
└── README.md                     # Project documentation 
```

---

## Part 1: Parallel Sorting (MapReduce Style)

###  Description
**Goal:** Sort a large array of integers in parallel using threads.

**Process:**
1. **Map Phase:** Divide the input array into equal chunks.
2. Each worker thread sorts its chunk using Merge Sort or Quick Sort.
3. **Reduce Phase:** A reducer thread merges all sorted chunks into one final sorted array.

###  Requirements
- Implemented using **multithreading**.
- Use shared data structures or queues to pass results between threads.
- Measure **execution time** and **memory usage** for 1, 2, 4, and 8 workers.

---

##  Part 2: Max-Value Aggregation with Constrained Shared Memory

###  Description
**Goal:** Compute the **global maximum** value using limited shared memory — only **one integer**.

**Process:**
1. **Map Phase:** Each worker computes the local maximum of its data chunk.
2. **Reduce Phase:** Workers compete to update a shared global maximum buffer.
3. Synchronization (locks/semaphores) ensures correctness.

###  Requirements
- Shared memory region must store **only one integer**.
- Proper synchronization to prevent race conditions.
- Measure runtime for 1, 2, 4, and 8 workers.

###  Implementations
- **`MaxValue_Thread.py`** — Uses threads and `threading.Lock`.
- **`MaxValue_Process.py`** — Uses processes and `multiprocessing.Value`.

---

##  How to Run the Project

###  Option 1 — Run in **PyCharm (Recommended)**
1. **Open the Project**
   - Launch PyCharm.
   - Click "Clone Repository" and paste the git URL.
   - The GitHub will then be loaded onto the interpreter.

2. **Choose the Script**
   - In the Project pane, open one of the files:
     - `ParallelSorting_Thread.py`
     - `ParallelSorting_Process.py`
     - `MaxValue_Thread.py`
     

3. **Set Up the Run Configuration**
   - Right-click the file and choose **Run '<filename>'**.
   - PyCharm will automatically create a run configuration for that code.

4. **View Output**
   - The program will run in the **Run Console** at the bottom.
   - You’ll see printed logs showing progress, execution time, and final output (sorted array or max value).

5. *(Optional)* — Adjust Inputs
   - The codes allow editing variables like array size or worker count directly at the bottom.

---

### Option 2 — Run from the **Command Line**
Open a terminal (inside PyCharm or your system terminal), navigate to the project directory, and run:

```bash
cd MapReduce_Project
```

Then execute one of the codes:

#### 1. Parallel Sorting (Threads)
```bash
python ParallelSorting_Thread.py
```

#### 2. Max-Value Aggregation (Threads)
```bash
python MaxValue_Thread.py
```

##  Example Output

###  Parallel Sorting Example
```
Running parallel sort with 4 threads...
Map phase completed in 0.034s
Reduce phase completed in 0.012s
Total time: 0.046s
```

###  Max-Value Aggregation Example
```
Starting with 8 worker threads...
Global max found: 999999
Total execution time: 0.008s

```

## Diagrams 
Multithreading: 
+-----------------------------------------------------------+
|                    Main Thread (Coordinator)              |
|-----------------------------------------------------------|
| 1. Splits input data into chunks                          |
| 2. Spawns worker threads (Map Phase)                      |
| 3. Waits for threads to finish sorting/aggregation         |
| 4. Launches reducer thread to merge or finalize results    |
+-----------------------------------------------------------+
                 |          |          |          |
                 v          v          v          v
        +-----------+ +-----------+ +-----------+ +-----------+
        | MapThread1| | MapThread2| | MapThread3| | MapThread4|
        +-----------+ +-----------+ +-----------+ +-----------+
                 \         |          |          /
                  \        |          |         /
                   \_______|__________|________/
                            IPC via
                   Shared Variables / Queues
                              ↓
                   +---------------------------+
                   |       Reducer Thread      |
                   |  - Merges sorted chunks   |
                   |  - Or computes global max |
                   +---------------------------+
Multi-processing:
+-----------------------------------------------------------+
|                 Main Process (Coordinator)                |
|-----------------------------------------------------------|
| - Generates random input data                            |
| - Splits data into chunks                                 |
| - Creates N worker processes (Map phase)                  |
| - Collects sorted chunks from Queue                       |
| - Merges sorted chunks using heapq.merge() (Reduce phase) |
+-----------------------------------------------------------+
                 |            |            |            |
                 v            v            v            v
        +-------------+ +-------------+ +-------------+ +-------------+
        |  Worker 1   | |  Worker 2   | |  Worker 3   | |  Worker 4   |
        |-------------| |-------------| |-------------| |-------------|
        | Sorts its   | | Sorts its   | | Sorts its   | | Sorts its   |
        | data slice  | | data slice  | | data slice  | | data slice  |
        | using       | | using       | | using       | | using       |
        | sorted()    | | sorted()    | | sorted()    | | sorted()    |
        +------+------+ +------+------+ +------+------+ +------+
               |                |                |             |
               +----------------+----------------+-------------+
                                |
                      Inter-Process Communication
                          via `multiprocessing.Queue`
                                |
                                v
                    +-------------------------------+
                    |        Reducer Stage           |
                    |-------------------------------|
                    | - Collects sorted slices      |
                    | - Merges all chunks with       |
                    |   heapq.merge()                |
                    | - Produces final sorted array  |
                    +-------------------------------+


##  References
- Dean, J., & Ghemawat, S. (2008). *MapReduce: Simplified Data Processing on Large Clusters.*
- Python Documentation:
  - [`threading`](https://docs.python.org/3/library/threading.html)
  - [`multiprocessing`](https://docs.python.org/3/library/multiprocessing.html)
  - [`time`](https://docs.python.org/3/library/time.html)
  - [`random`](https://docs.python.org/3/library/random.html)
