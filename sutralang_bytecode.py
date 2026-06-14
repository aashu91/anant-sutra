# SutraLang Bytecode Compiler
# Compiles plain text SutraLang files to .sutrab binary files

import sys
import struct
import re

# Opcode constants
OP_SRUJ = 0x01
OP_VRDH = 0x02
OP_HRAS = 0x03
OP_DRSH = 0x04
OP_YOG = 0x05
OP_ANTR = 0x06
OP_GUN = 0x07
OP_BHAG = 0x08
OP_SANDH = 0x09
OP_SANKALPA = 0x0A
OP_PRAVAH = 0x0B
OP_END_BLOCK = 0x0C
OP_GUNAN = 0x0D
OP_BHAGAPHALAM = 0x0E

# Comparison tag constants
COMP_BADA = 0x01
COMP_CHOTA = 0x02
COMP_BARABAR = 0x03

# Value type tags
TAG_INT = 0x01
TAG_STR = 0x02
TAG_VAR = 0x03

def translate_natural_prompt(line):
    l = line.strip()
    lower_l = l.lower()

    if lower_l in ("loop khatam", "end loop", "loop_khatam", "pravah_khatam"):
        return "pravah_khatam"
    if lower_l in ("sankalpa khatam", "end if", "sankalpa_khatam"):
        return "sankalpa_khatam"

    # Creation
    create_pat1 = r'ek\s+variable\s+banao\s+(\w+)\s+(?:value|maan)\s+((?:"[^"]*")|[\w\d]+)'
    create_pat2 = r'create\s+variable\s+(\w+)\s+with\s+(?:value|maan)\s+((?:"[^"]*")|[\w\d]+)'
    create_pat3 = r'banao\s+variable\s+(\w+)\s+(?:value|maan)\s+((?:"[^"]*")|[\w\d]+)'
    create_pat4 = r'ek\s+variable\s+(\w+)\s+(?:value|maan)\s+((?:"[^"]*")|[\w\d]+)'
    
    for pat in (create_pat1, create_pat2, create_pat3, create_pat4):
        m = re.search(pat, l, re.IGNORECASE)
        if m:
            return f"{m.group(1)} + sruj(maan={m.group(2)})"

    # Yog (Addition)
    yog_pat1 = r'(\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+aur\s+((?:"[^"]*")|[\w\d]+)\s+ka\s+yog\s+rkho'
    yog_pat2 = r'set\s+(\w+)\s+as\s+sum\s+of\s+((?:"[^"]*")|[\w\d]+)\s+and\s+((?:"[^"]*")|[\w\d]+)'
    for pat in (yog_pat1, yog_pat2):
        m = re.search(pat, l, re.IGNORECASE)
        if m:
            return f"{m.group(1)} + yog(karana={m.group(2)}, sahakarana={m.group(3)})"

    # Antar (Subtraction)
    antar_pat1 = r'(\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+aur\s+((?:"[^"]*")|[\w\d]+)\s+ka\s+antar\s+rkho'
    antar_pat2 = r'set\s+(\w+)\s+as\s+difference\s+of\s+((?:"[^"]*")|[\w\d]+)\s+and\s+((?:"[^"]*")|[\w\d]+)'
    for pat in (antar_pat1, antar_pat2):
        m = re.search(pat, l, re.IGNORECASE)
        if m:
            return f"{m.group(1)} + antar(karana={m.group(2)}, sahakarana={m.group(3)})"

    # Gunan (Multiplication)
    gunan_pat1 = r'(\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+aur\s+((?:"[^"]*")|[\w\d]+)\s+ka\s+gunan\s+rkho'
    gunan_pat2 = r'set\s+(\w+)\s+as\s+product\s+of\s+((?:"[^"]*")|[\w\d]+)\s+and\s+((?:"[^"]*")|[\w\d]+)'
    for pat in (gunan_pat1, gunan_pat2):
        m = re.search(pat, l, re.IGNORECASE)
        if m:
            return f"{m.group(1)} + gunan(karana={m.group(2)}, sahakarana={m.group(3)})"

    # Bhagaphalam (Division)
    bhag_pat1 = r'(\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+aur\s+((?:"[^"]*")|[\w\d]+)\s+ka\s+bhagaphalam\s+rkho'
    bhag_pat2 = r'set\s+(\w+)\s+as\s+division\s+of\s+((?:"[^"]*")|[\w\d]+)\s+and\s+((?:"[^"]*")|[\w\d]+)'
    for pat in (bhag_pat1, bhag_pat2):
        m = re.search(pat, l, re.IGNORECASE)
        if m:
            return f"{m.group(1)} + bhagaphalam(karana={m.group(2)}, sahakarana={m.group(3)})"

    # Sandh (String Concatenation)
    sandh_pat1 = r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+aur\s+((?:"[^"]*")|\w+)\s+se\s+jodo'
    sandh_pat2 = r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+aur\s+((?:"[^"]*")|\w+)\s+ka\s+sandhi\s+rkho'
    sandh_pat3 = r'set\s+(\w+)\s+as\s+concatenation\s+of\s+((?:"[^"]*")|\w+)\s+and\s+((?:"[^"]*")|\w+)'
    for pat in (sandh_pat1, sandh_pat2, sandh_pat3):
        m = re.search(pat, l, re.IGNORECASE)
        if m:
            return f"{m.group(1)} + sandh(karana={m.group(2)}, sahakarana={m.group(3)})"

    # Vardhanam (Increment)
    inc_pat1 = r'(\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+se\s+badhao'
    inc_pat2 = r'add\s+((?:"[^"]*")|[\w\d]+)\s+to\s+(\w+)'
    inc_pat3 = r'(\w+)\s+me\s+((?:"[^"]*")|[\w\d]+)\s+(?:jod|add)'
    m = re.search(inc_pat1, l, re.IGNORECASE)
    if m: return f"{m.group(1)} + vrdh(karana={m.group(2)})"
    m = re.search(inc_pat2, l, re.IGNORECASE)
    if m: return f"{m.group(2)} + vrdh(karana={m.group(1)})"
    m = re.search(inc_pat3, l, re.IGNORECASE)
    if m: return f"{m.group(1)} + vrdh(karana={m.group(2)})"

    # Hrasanam (Decrement)
    dec_pat1 = r'(\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+se\s+kam\s+karo'
    dec_pat2 = r'subtract\s+((?:"[^"]*")|[\w\d]+)\s+from\s+(\w+)'
    dec_pat3 = r'(\w+)\s+se\s+((?:"[^"]*")|[\w\d]+)\s+(?:kam|minus|ghata)'
    m = re.search(dec_pat1, l, re.IGNORECASE)
    if m: return f"{m.group(1)} + hras(karana={m.group(2)})"
    m = re.search(dec_pat2, l, re.IGNORECASE)
    if m: return f"{m.group(2)} + hras(karana={m.group(1)})"
    m = re.search(dec_pat3, l, re.IGNORECASE)
    if m: return f"{m.group(1)} + hras(karana={m.group(2)})"

    # Darshanam (Display)
    show_pat1 = r'(.+)\s+ko\s+(?:dikhao|darshan|print)'
    show_pat2 = r'show\s+(.+)'
    show_pat3 = r'print\s+(.+)'
    show_pat4 = r'(.+)\s+(?:show|print)\s+karo'
    for pat in (show_pat1, show_pat2, show_pat3, show_pat4):
        m = re.search(pat, l, re.IGNORECASE)
        if m:
            return f"{m.group(1)} + drsh()"

    # Pravahanam (Loop)
    loop_pat1 = r'loop\s+chalao\s+jab\s+tak\s+(\w+)\s+((?:"[^"]*")|[\w\d]+)\s+se\s+chota'
    loop_pat2 = r'while\s+(\w+)\s+is\s+less\s+than\s+((?:"[^"]*")|[\w\d]+)'
    for pat in (loop_pat1, loop_pat2):
        m = re.search(pat, l, re.IGNORECASE)
        if m:
            return f"{m.group(1)} + pravah(seema={m.group(2)})"

    # Guna (Inline multiply)
    mult_pat1 = r'(\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+se\s+guna\s+karo'
    mult_pat2 = r'multiply\s+(\w+)\s+by\s+((?:"[^"]*")|[\w\d]+)'
    for pat in (mult_pat1, mult_pat2):
        m = re.search(pat, l, re.IGNORECASE)
        if m:
            return f"{m.group(1)} + gun(karana={m.group(2)})"

    # Bhaga (Inline divide)
    div_pat1 = r'(\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+se\s+bhag\s+do'
    div_pat2 = r'divide\s+(\w+)\s+by\s+((?:"[^"]*")|[\w\d]+)'
    for pat in (div_pat1, div_pat2):
        m = re.search(pat, l, re.IGNORECASE)
        if m:
            return f"{m.group(1)} + bhag(karana={m.group(2)})"

    # Sankalpa (Conditionals)
    cond_pat1 = r'agar\s+(\w+)\s+((?:"[^"]*")|[\w\d]+)\s+se\s+bada\s+ho'
    cond_pat2 = r'agar\s+(\w+)\s+((?:"[^"]*")|[\w\d]+)\s+se\s+chota\s+ho'
    cond_pat3 = r'agar\s+(\w+)\s+((?:"[^"]*")|[\w\d]+)\s+(?:ke\s+barabar|barabar)\s+ho'
    cond_pat4 = r'if\s+(\w+)\s+is\s+greater\s+than\s+((?:"[^"]*")|[\w\d]+)'
    cond_pat5 = r'if\s+(\w+)\s+is\s+less\s+than\s+((?:"[^"]*")|[\w\d]+)'
    cond_pat6 = r'if\s+(\w+)\s+is\s+equal\s+to\s+((?:"[^"]*")|[\w\d]+)'
    
    for pat, sharta in ((cond_pat1, "bada"), (cond_pat4, "bada")):
        m = re.search(pat, l, re.IGNORECASE)
        if m: return f"{m.group(1)} + sankalpa(sharta=bada, karana={m.group(2)})"
    for pat, sharta in ((cond_pat2, "chota"), (cond_pat5, "chota")):
        m = re.search(pat, l, re.IGNORECASE)
        if m: return f"{m.group(1)} + sankalpa(sharta=chota, karana={m.group(2)})"
    for pat, sharta in ((cond_pat3, "barabar"), (cond_pat6, "barabar")):
        m = re.search(pat, l, re.IGNORECASE)
        if m: return f"{m.group(1)} + sankalpa(sharta=barabar, karana={m.group(2)})"

    return l

def encode_string(s):
    b = s.encode('utf-8')
    return struct.pack('<H', len(b)) + b

def encode_value(val_str):
    val_str = val_str.strip()
    if val_str.startswith('"') and val_str.endswith('"'):
        content = val_str[1:-1]
        return struct.pack('B', TAG_STR) + encode_string(content)
    try:
        val_int = int(val_str)
        return struct.pack('B', TAG_INT) + struct.pack('<i', val_int)
    except ValueError:
        return struct.pack('B', TAG_VAR) + encode_string(val_str)

def compile_line_to_bytecode(line, line_num):
    # Auto-translate natural vibe coding to pure Paninian if no '+' exists
    if '+' not in line and line not in ("pravah_khatam", "sankalpa_khatam"):
        translated = translate_natural_prompt(line)
        if translated == line:
            raise SyntaxError(f"Line {line_num}: Unrecognized syntax: '{line}'")
        line = translated

    if line == "pravah_khatam" or line == "sankalpa_khatam":
        return struct.pack('B', OP_END_BLOCK)

    parts = line.split('+', 1)
    karta = parts[0].strip()
    right = parts[1].strip()

    open_p = right.find('(')
    close_p = right.find(')')
    if open_p == -1 or close_p == -1 or close_p < open_p:
        raise SyntaxError(f"Line {line_num}: Invalid Dhatu/Pratyaya syntax in '{right}'")

    kriya = right[:open_p].strip().lower()
    args_str = right[open_p+1:close_p].strip()

    args = {}
    if args_str:
        for pair in args_str.split(','):
            if '=' in pair:
                k, v = pair.split('=', 1)
                args[k.strip()] = v.strip()

    if kriya == "sruj":
        return struct.pack('B', OP_SRUJ) + encode_string(karta) + encode_value(args.get("maan", "0"))
    elif kriya == "vrdh":
        return struct.pack('B', OP_VRDH) + encode_string(karta) + encode_value(args.get("karana", "1"))
    elif kriya == "hras":
        return struct.pack('B', OP_HRAS) + encode_string(karta) + encode_value(args.get("karana", "1"))
    elif kriya == "drsh":
        # Darshanam can print either variable or literal
        return struct.pack('B', OP_DRSH) + encode_value(karta)
    elif kriya == "yog":
        return struct.pack('B', OP_YOG) + encode_string(karta) + encode_value(args.get("karana")) + encode_value(args.get("sahakarana"))
    elif kriya == "antar":
        return struct.pack('B', OP_ANTR) + encode_string(karta) + encode_value(args.get("karana")) + encode_value(args.get("sahakarana"))
    elif kriya == "gun":
        return struct.pack('B', OP_GUN) + encode_string(karta) + encode_value(args.get("karana", "1"))
    elif kriya == "bhag":
        return struct.pack('B', OP_BHAG) + encode_string(karta) + encode_value(args.get("karana", "1"))
    elif kriya == "sandh":
        return struct.pack('B', OP_SANDH) + encode_string(karta) + encode_value(args.get("karana")) + encode_value(args.get("sahakarana"))
    elif kriya == "gunan":
        return struct.pack('B', OP_GUNAN) + encode_string(karta) + encode_value(args.get("karana")) + encode_value(args.get("sahakarana"))
    elif kriya == "bhagaphalam":
        return struct.pack('B', OP_BHAGAPHALAM) + encode_string(karta) + encode_value(args.get("karana")) + encode_value(args.get("sahakarana"))
    elif kriya == "sankalpa":
        sharta = args.get("sharta", "barabar")
        sharta_tag = COMP_BARABAR
        if sharta == "bada": sharta_tag = COMP_BADA
        elif sharta == "chota": sharta_tag = COMP_CHOTA
        return struct.pack('B', OP_SANKALPA) + encode_string(karta) + struct.pack('B', sharta_tag) + encode_value(args.get("karana"))
    elif kriya == "pravah":
        return struct.pack('B', OP_PRAVAH) + encode_string(karta) + encode_value(args.get("seema"))
    else:
        raise SyntaxError(f"Line {line_num}: Unknown Dhatu action: '{kriya}'")

def compile_source_to_bytecode(text):
    lines = text.split('\n')
    bytecode = bytearray()
    
    bytecode.extend(b'SUTR') # Magic
    bytecode.append(0x01)   # Version 1

    in_loop_or_if = 0
    
    for idx, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith(';'):
            continue
        try:
            instr_bytes = compile_line_to_bytecode(line, idx)
            if instr_bytes:
                opcode = instr_bytes[0]
                if opcode in (OP_PRAVAH, OP_SANKALPA):
                    in_loop_or_if += 1
                elif opcode == OP_END_BLOCK:
                    in_loop_or_if -= 1
                    if in_loop_or_if < 0:
                        raise SyntaxError(f"Line {idx}: Orphan block end keyword.")
                bytecode.extend(instr_bytes)
        except Exception as e:
            print(f"Error compiling line {idx}: {e}")
            raise e
            
    if in_loop_or_if > 0:
        raise SyntaxError("Unterminated block(s) at end of program.")
        
    return bytes(bytecode)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 sutralang_bytecode.py <source.sutra> <output.sutrab>")
        sys.exit(1)
        
    src_path = sys.argv[1]
    dest_path = sys.argv[2]
    
    with open(src_path, 'r', encoding='utf-8') as f:
        src_text = f.read()
        
    try:
        binary_bytecode = compile_source_to_bytecode(src_text)
        with open(dest_path, 'wb') as f:
            f.write(binary_bytecode)
        print(f"Compilation successful: {src_path} -> {dest_path} ({len(binary_bytecode)} bytes)")
    except Exception as e:
        print(f"Compilation failed: {e}")
        sys.exit(1)
