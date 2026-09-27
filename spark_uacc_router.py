#!/usr/bin/env python3
"""
SparkUACC Router: Energy-Harvesting & Resource-Gated Computer Control Engine
Part of SutraOS Sovereign Brain ecosystem for Termux.

Manages low-overhead Xvfb virtual framebuffers, screenshot compression,
CPU/RAM circuit breaking, and intent-triggered spin-up for UACC / Computer Use MCP.
"""

import os
import sys
import time
import json
import subprocess
import shutil
import urllib.request

# ponytail: lightweight env and system load parser without third-party dependencies.
# Ceiling: Linux /proc filesystem. Upgrade path: psutil if cross-platform BSD needed.

MEMORY_FILE = "/data/data/com.termux/files/home/sutralang/sutra_memory.json"
DEFAULT_DISPLAY = os.environ.get("DISPLAY", ":0")
FRAMEBUFFER_RES = "1024x768x16" # 16-bit color depth for low RAM consumption (~15MB)

def load_env():
    env_files = [
        os.path.expanduser("/data/data/com.termux/files/home/.env"),
        os.path.expanduser("~/poly_v2/.env")
    ]
    env = {}
    for ef in env_files:
        if os.path.exists(ef):
            with open(ef, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        env[k.strip()] = v.strip()
    return env

ENV = load_env()
DISCORD_WEBHOOK_URL = ENV.get("DISCORD_WEBHOOK_URL")

class SparkUACCRouter:
    """Sparse Energy-Harvesting Router for UACC Desktop Controls."""

    def __init__(self, display: str = DEFAULT_DISPLAY):
        self.display = display
        self.xvfb_proc = None

    @staticmethod
    def get_system_health() -> dict:
        """Parses Linux /proc/meminfo and system load average."""
        mem_free_mb = 1000
        mem_total_mb = 4000
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
                mem_map = {}
                for l in lines:
                    parts = l.split(":")
                    if len(parts) == 2:
                        k = parts[0].strip()
                        v = parts[1].strip().split()[0]
                        mem_map[k] = int(v)
                mem_free_mb = mem_map.get("MemAvailable", mem_map.get("MemFree", 1000000)) // 1024
                mem_total_mb = mem_map.get("MemTotal", 4000000) // 1024
        except Exception:
            pass

        try:
            load_1m = os.getloadavg()[0]
        except Exception:
            load_1m = 0.5

        is_stressed = mem_free_mb < 400 or load_1m > 4.0

        return {
            "mem_available_mb": mem_free_mb,
            "mem_total_mb": mem_total_mb,
            "load_1m": load_1m,
            "is_stressed": is_stressed
        }

    def notify_discord(self, title: str, description: str, color: int = 10181046):
        """Sends log notification to Discord."""
        if not DISCORD_WEBHOOK_URL:
            return False
        payload = {
            "username": "SparkUACC Governor",
            "embeds": [{
                "title": title,
                "description": description,
                "color": color,
                "footer": {"text": "SutraOS • Termux X11 Headless Engine"}
            }]
        }
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                DISCORD_WEBHOOK_URL,
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": "SparkUACC/1.0"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status in (200, 204)
        except Exception:
            return False

    def is_display_active(self) -> bool:
        """Checks if Xvfb display socket exists or is responding."""
        display_num = self.display.replace(":", "")
        socket_path = f"/tmp/.X11-unix/X{display_num}"
        return os.path.exists(socket_path)

    def spinup_display(self) -> bool:
        """Starts Xvfb virtual framebuffer on-demand if not active."""
        if self.is_display_active():
            return True

        xvfb_bin = shutil.which("Xvfb")
        if not xvfb_bin:
            print("[WARN] Xvfb is not installed. Run: pkg install xvfb")
            return False

        cmd = [xvfb_bin, self.display, "-screen", "0", FRAMEBUFFER_RES, "-ac"]
        try:
            self.xvfb_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.5)
            os.environ["DISPLAY"] = self.display
            print(f"[SparkUACC] Spinup Xvfb Virtual Framebuffer on {self.display} ({FRAMEBUFFER_RES})")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to start Xvfb: {e}")
            return False

    def hibernate_display(self):
        """Shuts down Xvfb to harvest CPU & RAM when idle."""
        if self.xvfb_proc and self.xvfb_proc.poll() is None:
            self.xvfb_proc.terminate()
            self.xvfb_proc.wait(timeout=2)
            print(f"[SparkUACC] Hibernated Xvfb on {self.display} (Resource Harvested)")
            self.xvfb_proc = None

    def execute_guarded_action(self, action_type: str, params: dict = None) -> dict:
        """Executes UACC action with resource gating & dynamic spin-up."""
        params = params or {}
        health = self.get_system_health()

        # Circuit Breaker: Throttling under heavy load
        if health["is_stressed"]:
            print(f"[WARN] System Stressed (Free RAM: {health['mem_available_mb']}MB, Load: {health['load_1m']}). Throttling...")
            time.sleep(0.5)

        # Dynamic Spin-up
        if not self.spinup_display():
            return {"status": "error", "message": "Xvfb display unavailable"}

        os.environ["DISPLAY"] = self.display
        result = {"status": "success", "action": action_type, "health": health}

        try:
            if action_type == "screenshot":
                tmp_dir = os.environ.get("TMPDIR", "/data/data/com.termux/files/usr/tmp")
                out_path = params.get("output", os.path.join(tmp_dir, "spark_uacc_screen.png"))
                scrot_bin = shutil.which("scrot")
                if scrot_bin:
                    subprocess.run([scrot_bin, "-z", out_path], check=True)
                else:
                    # Fallback using xwd or import if available
                    result["status"] = "warning"
                    result["message"] = "scrot not found, install using: pkg install scrot"

                result["output_file"] = out_path

            elif action_type == "mouse_click":
                x = params.get("x", 0)
                y = params.get("y", 0)
                xdotool_bin = shutil.which("xdotool")
                if xdotool_bin:
                    subprocess.run([xdotool_bin, "mousemove", str(x), str(y), "click", "1"], check=True)
                    result["message"] = f"Clicked at ({x}, {y})"
                else:
                    result["status"] = "warning"
                    result["message"] = "xdotool not found, install using: pkg install xdotool"

            elif action_type == "type_text":
                text = params.get("text", "")
                xdotool_bin = shutil.which("xdotool")
                if xdotool_bin:
                    subprocess.run([xdotool_bin, "type", text], check=True)
                    result["message"] = f"Typed '{text}'"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        # Notify Discord
        self.notify_discord(
            title=f"🖥️ SparkUACC Action: {action_type}",
            description=f"**Status**: `{result['status']}`\n**RAM Free**: `{health['mem_available_mb']}MB` | **Load**: `{health['load_1m']}`\n**Details**: `{result.get('message', 'Completed')}`",
            color=65280 if result["status"] == "success" else 16753920
        )

        return result


if __name__ == "__main__":
    router = SparkUACCRouter()
    health = SparkUACCRouter.get_system_health()
    print(f"--- SparkUACC Health Check ---")
    print(f"RAM Available: {health['mem_available_mb']} MB / {health['mem_total_mb']} MB")
    print(f"1-Min System Load: {health['load_1m']}")
    print(f"System Stressed: {health['is_stressed']}")
    
    tmp_dir = os.environ.get("TMPDIR", "/data/data/com.termux/files/usr/tmp")
    res = router.execute_guarded_action("screenshot", {"output": os.path.join(tmp_dir, "uacc_demo.png")})
    print(f"Action Result: {json.dumps(res, indent=2)}")
    
    # Clean hibernation test
    router.hibernate_display()
    assert not router.is_display_active(), "Display should be hibernated"
    print("Self-check passed cleanly!")
