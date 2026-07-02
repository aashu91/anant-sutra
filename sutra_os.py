# SutraOS: Virtualized Paninian Operating System Simulation
# Implements Ramanujan Expander Scheduler and Nyaya Logic Page Table

import random
import math

class ExpanderScheduler:
    def __init__(self):
        # 3-regular hypercube graph with 8 nodes (cores)
        # Represents virtual CPU execution units
        self.cores = {
            0: [1, 2, 4],
            1: [0, 3, 5],
            2: [0, 3, 6],
            3: [1, 2, 7],
            4: [0, 5, 6],
            5: [1, 4, 7],
            6: [2, 4, 7],
            7: [3, 5, 6]
        }
        # Active tasks mapping: Core ID -> List of task names
        self.load = {i: [] for i in range(8)}
        # Track scheduling history
        self.history = []

    def get_spectral_gap(self) -> dict:
        """Returns the spectral gap metrics of the 3-regular expander hypercube graph."""
        # For a d-regular graph, the spectral gap determines the mixing rate:
        # lambda_2 <= 2 * sqrt(d - 1)
        # For our 3-regular hypercube: d = 3.
        # Adjacency eigenvalues: 3 (mult 1), 1 (mult 3), -1 (mult 3), -3 (mult 1)
        # Second largest eigenvalue (lambda_2) is 1.
        # Spectral gap = d - lambda_2 = 3 - 1 = 2.
        # Ramanujan Bound: 2 * sqrt(2) = 2.828.
        # Since lambda_2 (1) <= 2.828, it satisfies the Ramanujan expander bound!
        return {
            "degree": 3,
            "lambda_2": 1.0,
            "ramanujan_bound": round(2 * math.sqrt(2), 3),
            "spectral_gap": 2.0,
            "is_ramanujan": True
        }

    def add_task(self, task_name: str) -> int:
        """Spawns a task on a random core and returns the starting core ID."""
        # Place task on a random starting core
        start_core = random.randint(0, 7)
        self.load[start_core].append(task_name)
        self.history.append(f"Task '{task_name}' spawned on Core {start_core}")
        return start_core

    def tick(self) -> list:
        """Runs one scheduling cycle using decentralized load-balancing walk on the expander."""
        # Run one scheduling step using decentralized load-balancing walk:
        # Each task evaluates neighbors and moves to the neighbor with the minimum load
        new_load = {i: [] for i in range(8)}
        movements = []

        for core_id, tasks in self.load.items():
            for task in tasks:
                neighbors = self.cores[core_id]
                # Find neighbor with least current load
                best_neighbor = core_id
                min_load = len(self.load[core_id])
                
                for n in neighbors:
                    n_load = len(self.load[n])
                    if n_load < min_load:
                        min_load = n_load
                        best_neighbor = n
                
                new_load[best_neighbor].append(task)
                if best_neighbor != core_id:
                    movements.append(f"Task '{task}': Core {core_id} ➔ Core {best_neighbor} (load balance)")
                else:
                    movements.append(f"Task '{task}': Stays on Core {core_id} (steady state)")
        
        self.load = new_load
        self.history.extend(movements)
        if len(self.history) > 30:
            self.history = self.history[-30:]
        return movements

class NyayaPageTable:
    def __init__(self):
        self.allocations = {} # Process -> Allocated Size
        self.logs = []

    def allocate(self, process_name: str, requested_size: int, buffer_limit: int) -> dict:
        """Allocates memory to a process using a 5-step Nyaya Pancavayava Syllogism validation."""
        requested_size = int(requested_size)
        buffer_limit = int(buffer_limit)

        # 5-step Nyaya Pancavayava Syllogism
        steps = [
            f"1. Pratijñā (Proposition): Allocation of {requested_size} bytes to '{process_name}' is safe.",
            f"2. Hetu (Reason): Because the maximum buffer limit of '{process_name}' is verified as {buffer_limit} bytes.",
            f"3. Udāharaṇa (Verification Example): Just like standard buffer operations where allocation size must equal or exceed buffer limit.",
            f"4. Upanaya (Application): The requested size ({requested_size} bytes) is " + ("greater than or equal to" if requested_size >= buffer_limit else "less than") + f" the buffer limit ({buffer_limit} bytes).",
            f"5. Nigamana (Conclusion): Therefore, this allocation is " + ("APPROVED (Memory Safe)." if requested_size >= buffer_limit else "DENIED (Buffer Overflow Risk!).")
        ]

        success = requested_size >= buffer_limit
        if success:
            self.allocations[process_name] = requested_size
        
        log_entry = {
            "process": process_name,
            "requested": requested_size,
            "limit": buffer_limit,
            "success": success,
            "syllogism": steps
        }
        self.logs.append(log_entry)
        if len(self.logs) > 20:
            self.logs = self.logs[-20:]
            
        return log_entry

if __name__ == "__main__":
    # Test simulation
    print("Testing Ramanujan Expander Scheduler...")
    scheduler = ExpanderScheduler()
    scheduler.add_task("CompilerProcess")
    scheduler.add_task("VMExecution")
    scheduler.add_task("VoiceListener")
    
    print("Initial loads:", {k: len(v) for k, v in scheduler.load.items()})
    scheduler.tick()
    print("Loads after tick 1:", {k: len(v) for k, v in scheduler.load.items()})
    
    print("\nTesting Nyaya Page Table...")
    pt = NyayaPageTable()
    res1 = pt.allocate("SutraVM", 1024, 512)
    print("Success:", res1["success"])
    for s in res1["syllogism"]:
        print(s)
        
    res2 = pt.allocate("ExploitThread", 128, 512)
    print("\nSuccess:", res2["success"])
    for s in res2["syllogism"]:
        print(s)
