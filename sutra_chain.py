import os
import sys
import json
import time
import hashlib
import subprocess

# Termux color outputs
COLOR_RESET   = "\033[0m"
COLOR_YELLOW  = "\033[93m"
COLOR_GREEN   = "\033[92m"
COLOR_BLUE    = "\033[94m"
COLOR_CYAN    = "\033[96m"
COLOR_RED     = "\033[91m"

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".sutrachain")
BLOCKS_DIR = os.path.join(BASE_DIR, "blocks")
STATE_FILE = os.path.join(BASE_DIR, "state.json")
PEERS_FILE = os.path.join(BASE_DIR, "peers.json")

os.makedirs(BLOCKS_DIR, exist_ok=True)

# Default configuration initialization
def init_state():
    if not os.path.exists(STATE_FILE):
        state = {
            "satya_points": {
                "operator": 10  # Seed operator with some initial validation points
            },
            "chain_length": 0,
            "last_block_hash": "0000000000000000000000000000000000000000000000000000000000000000"
        }
        save_state(state)
    if not os.path.exists(PEERS_FILE):
        peers = ["sutranodeexample1.onion", "sutranodeexample2.onion"]
        with open(PEERS_FILE, 'w') as f:
            json.dump(peers, f, indent=2)

def load_state():
    init_state()
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def load_peers():
    init_state()
    try:
        with open(PEERS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def get_block_paths(index):
    sutra_path = os.path.join(BLOCKS_DIR, f"block_{index:06d}.sutra")
    sutrab_path = os.path.join(BLOCKS_DIR, f"block_{index:06d}.sutrab")
    return sutra_path, sutrab_path

# Execute bytecode using native VM and extract stdout variables
def execute_block_vm(sutrab_path):
    cpp_vm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sutra")
    if not os.path.exists(cpp_vm_path):
        raise RuntimeError("Sutra VM binary not found. Compile it using: g++ -O3 -std=c++17 sutralang.cpp -o sutra")
    
    res = subprocess.run([cpp_vm_path, "--run", sutrab_path], capture_output=True, text=True, timeout=5)
    if res.returncode != 0:
        raise RuntimeError(f"VM runtime execution failed: {res.stderr.strip()}")
    
    # Parse VM stdout to restore register state values
    lines = res.stdout.split("\n")
    variables = {}
    for line in lines:
        if "Srujana: Created variable" in line or "Mudra: Computed" in line:
            # Parse logs like: [SutraVM] Srujana: Created variable 'block_index' with Maan = 1
            parts = line.split(" variable '") if "Srujana: Created variable" in line else line.split(" set '")
            if len(parts) > 1:
                name_val = parts[1].split("' with Maan = ") if "Srujana: Created variable" in line else parts[1].split("' = ")
                if len(name_val) > 1:
                    var_name = name_val[0].strip()
                    var_val = name_val[1].strip().strip('"')
                    variables[var_name] = var_val
    return variables

# Verify block integrity
def verify_block(index, prev_hash):
    _, sutrab_path = get_block_paths(index)
    if not os.path.exists(sutrab_path):
        return False, "Bytecode block file does not exist."
    
    # 1. Compute file hash
    with open(sutrab_path, 'rb') as f:
        file_bytes = f.read()
    block_hash = hashlib.sha256(file_bytes).hexdigest()
    
    # 2. Verify target difficulty
    # Parse state variables from bytecode run
    try:
        vars = execute_block_vm(sutrab_path)
    except Exception as e:
        return False, f"Bytecode validation execution failed: {e}"
    
    contributor = vars.get("contributor", "unknown")
    state = load_state()
    points = state["satya_points"].get(contributor, 0)
    
    # Dynamic difficulty check
    required_zeros = 4
    if points >= 10:
        required_zeros = 1
    elif points >= 5:
        required_zeros = 2
    elif points >= 1:
        required_zeros = 3
        
    target_prefix = "0" * required_zeros
    if not block_hash.startswith(target_prefix):
        return False, f"Block hash '{block_hash}' does not satisfy target difficulty of {required_zeros} leading zeroes."
    
    # 3. Check logical hierarchy links
    if int(vars.get("block_index", -1)) != index:
        return False, f"Block index mismatch: expected {index}, got {vars.get('block_index')}"
        
    if index > 0 and vars.get("prev_hash") != prev_hash:
        return False, f"Blockchain linkage broken: expected previous hash '{prev_hash}', got '{vars.get('prev_hash')}'"
        
    return True, block_hash

# Write a block script template to disk
def write_block_template(sutra_path, index, prev_hash, x, y, z, status, claim, proof, contributor, nonce):
    template = f"""; SutraChain Block Statement
ek variable block_index value {index}
ek variable prev_hash value "{prev_hash}"
ek variable voxel_x value {x}
ek variable voxel_y value {y}
ek variable voxel_z value {z}
ek variable truth_status value "{status}"
ek variable claim_summary value "{claim}"
ek variable proof_syllogism value "{proof}"
ek variable contributor value "{contributor}"
ek variable nonce value {nonce}

; State printouts for verification
print block_index
print prev_hash
print truth_status
print claim_summary
print proof_syllogism
print contributor
"""
    with open(sutra_path, 'w', encoding='utf-8') as f:
        f.write(template)

# Compile block script to bytecode
def compile_block(sutra_path, sutrab_path):
    cpp_vm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sutra")
    res = subprocess.run([cpp_vm_path, "--compile", sutra_path, sutrab_path], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Block compiler error: {res.stderr.strip()}")

# Mine block nonce loop
def mine_block(x, y, z, status, claim, proof, contributor="operator"):
    state = load_state()
    next_index = state["chain_length"]
    prev_hash = state["last_block_hash"]
    
    points = state["satya_points"].get(contributor, 0)
    required_zeros = 4
    if points >= 10:
        required_zeros = 1
    elif points >= 5:
        required_zeros = 2
    elif points >= 1:
        required_zeros = 3
        
    target_prefix = "0" * required_zeros
    
    print(f"{COLOR_CYAN}[Miner] Starting Proof-of-Useful-Work Miner...{COLOR_RESET}")
    print(f"  • Index: {next_index}")
    print(f"  • Coordinates: ({x}, {y}, {z})")
    print(f"  • Contributor: '{contributor}' (Satya Points: {points})")
    print(f"  • Hashing Difficulty Target: {required_zeros} leading zeroes ('{target_prefix}')")
    
    sutra_path, sutrab_path = get_block_paths(next_index)
    nonce = 0
    start_time = time.time()
    
    while True:
        # 1. Write script template
        write_block_template(sutra_path, next_index, prev_hash, x, y, z, status, claim, proof, contributor, nonce)
        # 2. Compile to binary bytecode
        try:
            compile_block(sutra_path, sutrab_path)
        except Exception as e:
            print(f"Compilation failure: {e}")
            break
            
        # 3. Read binary bytes and check SHA-256 hash
        with open(sutrab_path, 'rb') as f:
            file_bytes = f.read()
        block_hash = hashlib.sha256(file_bytes).hexdigest()
        
        if block_hash.startswith(target_prefix):
            elapsed = time.time() - start_time
            print(f"{COLOR_GREEN}✔ Block Mined Successfully in {elapsed:.2f}s! Nonce: {nonce}{COLOR_RESET}")
            print(f"  • Hash: {block_hash}")
            
            # Update state database
            state["chain_length"] += 1
            state["last_block_hash"] = block_hash
            # Award miner 1 Satya Point for their successful validation addition
            state["satya_points"][contributor] = state["satya_points"].get(contributor, 0) + 1
            save_state(state)
            return True, block_hash
            
        nonce += 1
        if nonce % 500 == 0:
            print(f"  ... checked {nonce} hashes ...")

# Verify local chain consistency from index 0
def verify_full_chain():
    state = load_state()
    length = state["chain_length"]
    current_prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    
    print(f"{COLOR_BLUE}[Chain Verifier] Auditing blockchain state integrity...{COLOR_RESET}")
    for idx in range(length):
        ok, res_hash = verify_block(idx, current_prev_hash)
        if not ok:
            print(f"{COLOR_RED}❌ Chain Integrity Compromised at block {idx}: {res_hash}{COLOR_RESET}")
            return False
        current_prev_hash = res_hash
    print(f"{COLOR_GREEN}✔ Chain validation complete. All {length} blocks verified successfully.{COLOR_RESET}")
    return True

# Initialize Genesis block
def create_genesis():
    state = load_state()
    if state["chain_length"] == 0:
        print(f"{COLOR_YELLOW}[Chain] Empty state. Creating Genesis Block 0...{COLOR_RESET}")
        mine_block(
            x=0, y=0, z=0,
            status="verified",
            claim="SutraOS Blockchain Genesis Node",
            proof="AOC Initialized. Native Paninian code space validated.",
            contributor="operator"
        )

# Fetch JSON summary of all blocks (for Three.js visualizer)
def get_chain_json():
    create_genesis()
    state = load_state()
    length = state["chain_length"]
    blocks = []
    
    for idx in range(length):
        sutra_path, sutrab_path = get_block_paths(idx)
        if os.path.exists(sutrab_path):
            try:
                vars = execute_block_vm(sutrab_path)
                with open(sutrab_path, 'rb') as f:
                    file_bytes = f.read()
                block_hash = hashlib.sha256(file_bytes).hexdigest()
                
                blocks.append({
                    "index": idx,
                    "hash": block_hash,
                    "prev_hash": vars.get("prev_hash"),
                    "x": int(vars.get("voxel_x", 0)),
                    "y": int(vars.get("voxel_y", 0)),
                    "z": int(vars.get("voxel_z", 0)),
                    "status": vars.get("truth_status", "unverified"),
                    "claim": vars.get("claim_summary", ""),
                    "proof": vars.get("proof_syllogism", ""),
                    "contributor": vars.get("contributor", "unknown"),
                    "nonce": int(vars.get("nonce", 0))
                })
            except Exception as e:
                print(f"Error parsing block {idx}: {e}")
def sync_with_peers():
    peers = load_peers()
    state = load_state()
    local_len = state["chain_length"]
    synced_blocks = 0
    
    for peer in peers:
        peer = peer.strip()
        if not peer or "example.onion" in peer:
            continue
        try:
            print(f"{COLOR_BLUE}[Sync] Querying peer {peer} via Tor SOCKS5...{COLOR_RESET}")
            cmd = ["curl", "--socks5-hostname", "127.0.0.1:9050", "-s", f"http://{peer}/api/chain/status"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode != 0:
                print(f"{COLOR_RED}  • Failed to connect: {res.stderr.strip()}{COLOR_RESET}")
                continue
                
            peer_status = json.loads(res.stdout)
            peer_len = peer_status.get("chain_length", 0)
            
            if peer_len > local_len:
                print(f"{COLOR_GREEN}  • Peer has longer chain: {peer_len} vs {local_len}. Syncing...{COLOR_RESET}")
                for idx in range(local_len, peer_len):
                    block_url = f"http://{peer}/api/chain/block/{idx}"
                    sutra_path, sutrab_path = get_block_paths(idx)
                    
                    # Fetch block compiled bytecode
                    cmd_bin = ["curl", "--socks5-hostname", "127.0.0.1:9050", "-s", "-o", sutrab_path, block_url]
                    res_bin = subprocess.run(cmd_bin, capture_output=True, timeout=15)
                    if res_bin.returncode != 0 or not os.path.exists(sutrab_path) or os.path.getsize(sutrab_path) == 0:
                        print(f"{COLOR_RED}  • Failed to fetch block {idx}{COLOR_RESET}")
                        break
                        
                    # Fetch block source
                    block_src_url = f"http://{peer}/api/chain/block_src/{idx}"
                    subprocess.run(["curl", "--socks5-hostname", "127.0.0.1:9050", "-s", "-o", sutra_path, block_src_url], capture_output=True, timeout=5)
                    
                    # Verify block locally
                    prev_hash = state["last_block_hash"]
                    ok, res_hash = verify_block(idx, prev_hash)
                    if ok:
                        state["chain_length"] += 1
                        state["last_block_hash"] = res_hash
                        try:
                            vars = execute_block_vm(sutrab_path)
                            contrib = vars.get("contributor", "unknown")
                            state["satya_points"][contrib] = state["satya_points"].get(contrib, 0) + 1
                        except Exception:
                            pass
                        save_state(state)
                        local_len += 1
                        synced_blocks += 1
                        print(f"{COLOR_GREEN}  ✔ Validated and added block {idx} (Hash: {res_hash}){COLOR_RESET}")
                    else:
                        print(f"{COLOR_RED}  • Block {idx} validation failed: {res_hash}{COLOR_RESET}")
                        if os.path.exists(sutrab_path): os.remove(sutrab_path)
                        if os.path.exists(sutra_path): os.remove(sutra_path)
                        break
        except Exception as e:
            print(f"{COLOR_RED}  • Sync error: {e}{COLOR_RESET}")
            
    return synced_blocks

if __name__ == "__main__":
    create_genesis()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "mine":
            if len(sys.argv) < 8:
                print("Usage: python sutra_chain.py mine <x> <y> <z> <status> <claim> <proof> [contributor]")
                sys.exit(1)
            x, y, z = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
            status, claim, proof = sys.argv[5], sys.argv[6], sys.argv[7]
            contrib = sys.argv[8] if len(sys.argv) > 8 else "operator"
            mine_block(x, y, z, status, claim, proof, contrib)
        elif cmd == "verify":
            verify_full_chain()
        elif cmd == "sync":
            sync_with_peers()
        elif cmd == "status":
            st = load_state()
            print(f"SutraChain Status Board:")
            print(f"  • Chain Length: {st['chain_length']}")
            print(f"  • Last Block Hash: {st['last_block_hash']}")
            print(f"  • Active nodes: {load_peers()}")
            print(f"  • Satya Points ledger: {st['satya_points']}")
        else:
            print("Unknown command. Available commands: mine, verify, sync, status")
