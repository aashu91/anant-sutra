# ponytail: SWANS (Sovereign Workspace Auditor & Node Stamper)
# ceiling: O(N) memory/time scan overhead for huge trees. Upgrade path: use database or ignore files > 5MB.
import os
import sys
import json
import hashlib

STAMPS_FILE = "/data/data/com.termux/files/home/sutralang/.swans_stamps.json"
WORKSPACE_DIR = "/data/data/com.termux/files/home/sutralang"

BLACKLIST_DIRS = {
    '.git', '.npm', '.cache', '.bun', 'node_modules', '.gstack', 
    '.antigravitycli', '__pycache__', '.expo', 'venv', '.venv',
    'build', 'dist', 'out', '.next', 'temp_workspace'
}

def compute_hash(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return None

def stamp_workspace():
    stamps = {}
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        dirs[:] = [d for d in dirs if d not in BLACKLIST_DIRS]
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, WORKSPACE_DIR)
            h = compute_hash(filepath)
            if h:
                stamps[rel_path] = h
    try:
        with open(STAMPS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stamps, f, indent=2)
        return f"SWANS: Successfully stamped {len(stamps)} files."
    except Exception as e:
        return f"SWANS stamp failed: {e}"

def audit_workspace():
    if not os.path.exists(STAMPS_FILE):
        # Auto-initialize if stamps file does not exist
        stamp_workspace()
        return "SWANS: No previous stamps found. Initialized stamps."

    try:
        with open(STAMPS_FILE, 'r', encoding='utf-8') as f:
            stored = json.load(f)
    except Exception as e:
        return f"SWANS audit failed to read stamps: {e}"

    current = {}
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        dirs[:] = [d for d in dirs if d not in BLACKLIST_DIRS]
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, WORKSPACE_DIR)
            h = compute_hash(filepath)
            if h:
                current[rel_path] = h

    modified = []
    added = []
    deleted = []

    for path, h in current.items():
        if path not in stored:
            added.append(path)
        elif stored[path] != h:
            modified.append(path)

    for path in stored:
        if path not in current:
            deleted.append(path)

    if not modified and not added and not deleted:
        return "SWANS: Workspace is 100% clean. Zero modifications detected."

    report = ["SWANS Audit Report:"]
    if modified:
        report.append(f"  Modified ({len(modified)}): " + ", ".join(modified[:10]))
    if added:
        report.append(f"  Added ({len(added)}): " + ", ".join(added[:10]))
    if deleted:
        report.append(f"  Deleted ({len(deleted)}): " + ", ".join(deleted[:10]))
    
    return "\n".join(report)

# Runnable self-check
def test_swans():
    test_file = os.path.join(WORKSPACE_DIR, "temp_swans_test.txt")
    with open(test_file, "w") as f:
        f.write("swans initial state")
    try:
        # Stamp initial
        stamp_workspace()
        
        # Modify
        with open(test_file, "w") as f:
            f.write("swans modified state")
            
        audit = audit_workspace()
        assert "temp_swans_test.txt" in audit
        print("SWANS TEST PASSED")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
        stamp_workspace()  # Reset back to clean

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_swans()
    elif len(sys.argv) > 1 and sys.argv[1] == 'update':
        print(stamp_workspace())
    else:
        print(audit_workspace())
