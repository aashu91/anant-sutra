# SutraOS: Virtualized Paninian Operating System Simulation
# Implements Ramanujan Expander Scheduler, Nyaya Logic Page Table, IPC, Kshama Supervisor & Cognitive Router

import os
import subprocess
import random
import math
import collections

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
        return {
            "degree": 3,
            "lambda_2": 1.0,
            "ramanujan_bound": round(2 * math.sqrt(2), 3),
            "spectral_gap": 2.0,
            "is_ramanujan": True
        }

    def add_task(self, task_name: str) -> int:
        """Spawns a task on a random core and returns the starting core ID."""
        start_core = random.randint(0, 7)
        self.load[start_core].append(task_name)
        self.history.append(f"Task '{task_name}' spawned on Core {start_core}")
        return start_core

    def kill_task(self, task_name: str) -> bool:
        """Preemptively interrupts and evicts a running task from all core load queues.
        ponytail: In-memory task eviction; upgrade path: OS POSIX signals / PID termination.
        """
        removed = False
        for core_id, tasks in self.load.items():
            if task_name in tasks:
                self.load[core_id] = [t for t in tasks if t != task_name]
                removed = True
        if removed:
            self.history.append(f"SIGKILL (Preemptive Interrupt): Task '{task_name}' terminated")
        return removed

    def get_telemetry_snapshot(self) -> dict:
        """Returns detailed load breakdown and core connections for 3D visualizer telemetry."""
        return {
            "cores": self.cores,
            "load": self.load,
            "spectral_gap": self.get_spectral_gap(),
            "history": self.history[-15:],
            "active_tasks_count": sum(len(tasks) for tasks in self.load.values())
        }

    def tick(self) -> list:
        """Runs one scheduling cycle using decentralized load-balancing walk on the expander."""
        new_load = {i: [] for i in range(8)}
        movements = []

        for core_id, tasks in self.load.items():
            for task in tasks:
                neighbors = self.cores[core_id]
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


class SutraIPC:
    """Sovereign Inter-Process Communication bus for cross-core process messaging.
    ponytail: In-memory deque queue per channel; upgrade path: POSIX shared memory / Unix domain sockets.
    """
    def __init__(self):
        self.channels = collections.defaultdict(collections.deque)

    def send(self, channel: str, sender: str, payload: dict):
        self.channels[channel].append({"sender": sender, "payload": payload})
        if len(self.channels[channel]) > 50:
            self.channels[channel].popleft()

    def receive(self, channel: str) -> dict | None:
        if self.channels[channel]:
            return self.channels[channel].popleft()
        return None

    def get_recent_messages(self, channel: str = None, limit: int = 15) -> list:
        """Returns recent messages across channels without dequeuing them."""
        results = []
        if channel:
            items = list(self.channels.get(channel, []))
            for item in items[-limit:]:
                results.append({"channel": channel, **item})
        else:
            for ch, q in self.channels.items():
                for item in list(q)[-limit:]:
                    results.append({"channel": ch, **item})
        return results[-limit:]


class NyayaPageTable:
    def __init__(self):
        self.allocations = {} # Process -> Allocated Size
        self.capabilities = {} # Process -> Set of permissions {'read', 'write', 'net'}
        self.logs = []

    def allocate(self, process_name: str, requested_size: int, buffer_limit: int, cap_mask: set | None = None) -> dict:
        """Allocates memory and grants VFS/Net capability masks using Nyaya Pancavayava Syllogism validation.
        ponytail: Set-based capability checking in syllogism; upgrade path: eBPF / seccomp security profiles.
        """
        requested_size = int(requested_size)
        buffer_limit = int(buffer_limit)
        cap_mask = cap_mask or {"read"}

        steps = [
            f"1. Pratijñā (Proposition): Allocation of {requested_size} bytes with caps {cap_mask} to '{process_name}' is safe.",
            f"2. Hetu (Reason): Because maximum buffer limit is verified as {buffer_limit} bytes.",
            f"3. Udāharaṇa (Verification Example): Buffer allocation must exceed or equal limit and capabilities must be declared.",
            f"4. Upanaya (Application): Requested size ({requested_size} bytes) is " + ("greater than or equal to" if requested_size >= buffer_limit else "less than") + f" buffer limit ({buffer_limit} bytes).",
            f"5. Nigamana (Conclusion): Therefore, this allocation is " + ("APPROVED (Memory & Access Safe)." if requested_size >= buffer_limit else "DENIED (Buffer Overflow Risk!).")
        ]

        success = requested_size >= buffer_limit
        if success:
            self.allocations[process_name] = requested_size
            self.capabilities[process_name] = cap_mask
        
        log_entry = {
            "process": process_name,
            "requested": requested_size,
            "limit": buffer_limit,
            "success": success,
            "capabilities": list(cap_mask) if success else [],
            "syllogism": steps
        }
        self.logs.append(log_entry)
        if len(self.logs) > 20:
            self.logs = self.logs[-20:]
            
        return log_entry

    def check_capability(self, process_name: str, required_cap: str) -> bool:
        """Verifies if a process possesses the requested capability (VFS/Net sandbox)."""
        caps = self.capabilities.get(process_name, set())
        return required_cap in caps


class KshamaSupervisor:
    """Self-healing supervisor node that auto-restarts failed/preempted tasks.
    ponytail: Simple restart counter & fallback re-spawn; upgrade path: Erlang OTP supervision trees.
    """
    def __init__(self, scheduler: ExpanderScheduler):
        self.scheduler = scheduler
        self.restart_counts = collections.defaultdict(int)

    def handle_failure(self, task_name: str, max_retries: int = 3) -> bool:
        if self.restart_counts[task_name] < max_retries:
            self.restart_counts[task_name] += 1
            start_core = self.scheduler.add_task(task_name)
            self.scheduler.history.append(f"KshamaSupervisor: Auto-healed '{task_name}' -> Core {start_core} (Attempt {self.restart_counts[task_name]})")
            return True
        self.scheduler.history.append(f"KshamaSupervisor: Task '{task_name}' exceeded max retries ({max_retries}). Marked FAILED.")
        return False


class SutraCognitiveRouter:
    """Dynamic task router for latency and resource optimization.
    ponytail: Heuristic keyword & length routing; upgrade path: token estimator + dynamic benchmark routing.
    """
    @staticmethod
    def route_query(query: str) -> str:
        q = query.strip().lower()
        if any(k in q for k in ["ek ", "banao", "badhao", "print", "add ", "set ", "value "]):
            return "NATIVE_CPP_AST"
        elif len(q) < 300:
            return "LOCAL_OLLAMA_FLASH"
        else:
            return "CLOUD_HIGH_REASONING"


def run_native_sutraos() -> subprocess.CompletedProcess:
    """Invokes the standalone 100% Native SutraLang 3.0 ELF Engine binary (sutraos)."""
    native_bin = "/data/data/com.termux/files/home/sutralang_v3/sutraos"
    if not os.path.exists(native_bin):
        native_bin = "/data/data/com.termux/files/home/sutralang/sutraos"
    return subprocess.run([native_bin], check=True, text=True)


if __name__ == "__main__":
    # Runnable Ponytail Self-Check Verification Suite
    print("Running SutraOS Ponytail Verification Suite...")

    # 1. Expander Scheduler & Preemption Test
    scheduler = ExpanderScheduler()
    core_id = scheduler.add_task("CompilerProcess")
    assert any("CompilerProcess" in tasks for tasks in scheduler.load.values()), "Task should be loaded on a core"
    
    killed = scheduler.kill_task("CompilerProcess")
    assert killed is True, "Preemptive interrupt should succeed"
    assert not any("CompilerProcess" in tasks for tasks in scheduler.load.values()), "Task should be evicted from all cores"
    print("✓ Preemptive Interrupt Controller: PASSED")

    # 2. IPC Test
    ipc = SutraIPC()
    ipc.send("sys_events", "Core0", {"event": "HIGH_LOAD"})
    msg = ipc.receive("sys_events")
    assert msg is not None and msg["sender"] == "Core0", "IPC message delivery failed"
    assert ipc.receive("sys_events") is None, "IPC queue should be empty after pop"
    print("✓ Sovereign Inter-Process Communication (IPC): PASSED")

    # 3. Nyaya Page Table & Capability Sandboxing Test
    pt = NyayaPageTable()
    alloc = pt.allocate("SutraVM", 1024, 512, cap_mask={"read", "write"})
    assert alloc["success"] is True, "Memory allocation failed"
    assert pt.check_capability("SutraVM", "read") is True, "Read capability check failed"
    assert pt.check_capability("SutraVM", "net") is False, "Ungranted net capability should fail"
    print("✓ Nyaya Memory & Capability Sandbox: PASSED")

    # 4. Kshama Self-Healing Supervisor Test
    supervisor = KshamaSupervisor(scheduler)
    healed = supervisor.handle_failure("CrashedWorker")
    assert healed is True, "Supervisor should auto-heal task"
    assert any("CrashedWorker" in tasks for tasks in scheduler.load.values()), "Auto-healed task should be on scheduler"
    print("✓ Kshama Self-Healing Supervisor: PASSED")

    # 5. Cognitive Model Router Test
    assert SutraCognitiveRouter.route_query("ek variable x value 10") == "NATIVE_CPP_AST", "Simple AST route failed"
    assert SutraCognitiveRouter.route_query("What is the capital of India?") == "LOCAL_OLLAMA_FLASH", "Local LLM route failed"
    assert SutraCognitiveRouter.route_query("Explain quantum computing " * 20) == "CLOUD_HIGH_REASONING", "Cloud reasoning route failed"
    print("✓ Cognitive Model Router: PASSED")

    print("\nExecuting Standalone Native SutraOS 3.0 ELF Binary...\n")
    run_native_sutraos()
    print("\nALL SUTRAOS NATIVE PRIMITIVES VERIFIED SUCCESSFULLY!")



