# SutraLang Compiler: Translates Hinglish/English Vibe Prompts to Paninian AST
import re
import json

class SutraCompiler:
    def __init__(self):
        pass

    def log(self, message):
        print(f"[\033[96mSutraCompiler\033[0m] {message}")

    def compile_line(self, line):
        line = line.strip()
        if not line:
            return None

        # Pattern 1: Variable Creation (Srujana)
        match_create = re.search(
            r'ek\s+variable\s+banao\s+(\w+)\s+(?:value|maan)\s+((?:"[^"]*")|[\w\d]+)',
            line, re.IGNORECASE
        ) or re.search(
            r'create\s+variable\s+(\w+)\s+with\s+(?:value|maan)\s+((?:"[^"]*")|[\w\d]+)',
            line, re.IGNORECASE
        ) or re.search(
            r'banao\s+variable\s+(\w+)\s+(?:value|maan)\s+((?:"[^"]*")|[\w\d]+)',
            line, re.IGNORECASE
        ) or re.search(
            r'ek\s+variable\s+(\w+)\s+(?:value|maan)\s+((?:"[^"]*")|[\w\d]+)',
            line, re.IGNORECASE
        )
        if match_create:
            name = match_create.group(1)
            val_str = match_create.group(2)
            if val_str.startswith('"') and val_str.endswith('"'):
                val = val_str[1:-1]
            else:
                try:
                    val = int(val_str)
                except ValueError:
                    val = val_str
            return {"Kriya": "Srujana", "Karta": name, "Maan": val}

        # Yog (Addition)
        match_yog = re.search(r'(\w+)\s+ko\s+(\w+)\s+aur\s+(\w+)\s+ka\s+yog\s+rkho', line, re.IGNORECASE) or \
                    re.search(r'set\s+(\w+)\s+as\s+sum\s+of\s+(\w+)\s+and\s+(\w+)', line, re.IGNORECASE)
        if match_yog:
            return {"Kriya": "Yog", "Karta": match_yog.group(1), "Karana": match_yog.group(2), "Sahakarana": match_yog.group(3)}

        # Antar (Subtraction)
        match_antar = re.search(r'(\w+)\s+ko\s+(\w+)\s+aur\s+(\w+)\s+ka\s+antar\s+rkho', line, re.IGNORECASE) or \
                      re.search(r'set\s+(\w+)\s+as\s+difference\s+of\s+(\w+)\s+and\s+(\w+)', line, re.IGNORECASE)
        if match_antar:
            return {"Kriya": "Antar", "Karta": match_antar.group(1), "Karana": match_antar.group(2), "Sahakarana": match_antar.group(3)}

        # Gunan (Multiplication)
        match_gunan = re.search(r'(\w+)\s+ko\s+(\w+)\s+aur\s+(\w+)\s+ka\s+gunan\s+rkho', line, re.IGNORECASE) or \
                      re.search(r'set\s+(\w+)\s+as\s+product\s+of\s+(\w+)\s+and\s+(\w+)', line, re.IGNORECASE)
        if match_gunan:
            return {"Kriya": "Gunan", "Karta": match_gunan.group(1), "Karana": match_gunan.group(2), "Sahakarana": match_gunan.group(3)}

        # Bhagaphalam (Division)
        match_bhag = re.search(r'(\w+)\s+ko\s+(\w+)\s+aur\s+(\w+)\s+ka\s+bhagaphalam\s+rkho', line, re.IGNORECASE) or \
                     re.search(r'set\s+(\w+)\s+as\s+division\s+of\s+(\w+)\s+and\s+(\w+)', line, re.IGNORECASE)
        if match_bhag:
            return {"Kriya": "Bhagaphalam", "Karta": match_bhag.group(1), "Karana": match_bhag.group(2), "Sahakarana": match_bhag.group(3)}

        # Sandh (String Concatenation)
        match_sandh = re.search(r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+aur\s+((?:"[^"]*")|\w+)\s+se\s+jodo', line, re.IGNORECASE) or \
                      re.search(r'(\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+aur\s+((?:"[^"]*")|\w+)\s+ka\s+sandhi\s+rkho', line, re.IGNORECASE) or \
                      re.search(r'set\s+(\w+)\s+as\s+concatenation\s+of\s+((?:"[^"]*")|\w+)\s+and\s+((?:"[^"]*")|\w+)', line, re.IGNORECASE)
        if match_sandh:
            def clean_arg(s):
                if s.startswith('"') and s.endswith('"'):
                    return s[1:-1]
                return s
            return {"Kriya": "Sandh", "Karta": match_sandh.group(1), "Karana": clean_arg(match_sandh.group(2)), "Sahakarana": clean_arg(match_sandh.group(3))}

        # Pattern 2: Increment (Vardhanam)
        match_inc = re.search(
            r'(?:(\w+)\s+ko\s+(\w+)\s+se\s+badhao|add\s+(\w+)\s+to\s+(\w+)|(\w+)\s+me\s+(\w+)\s+(?:jod|add))',
            line, re.IGNORECASE
        )
        if match_inc:
            groups = [g for g in match_inc.groups() if g is not None]
            if len(groups) >= 2:
                if groups[0].isalpha() and groups[1].isdigit():
                    name = groups[0]
                    val = int(groups[1])
                elif groups[0].isdigit() and groups[1].isalpha():
                    val = int(groups[0])
                    name = groups[1]
                else:
                    name = groups[0]
                    try:
                        val = int(groups[1])
                    except ValueError:
                        val = groups[1]
                return {"Kriya": "Vardhanam", "Karma": name, "Karana": val}

        # Pattern 3: Decrement (Hrasanam)
        match_dec = re.search(
            r'(?:(\w+)\s+ko\s+(\w+)\s+se\s+kam\s+karo|subtract\s+(\w+)\s+from\s+(\w+)|(\w+)\s+se\s+(\w+)\s+(?:kam|minus|ghata))',
            line, re.IGNORECASE
        )
        if match_dec:
            groups = [g for g in match_dec.groups() if g is not None]
            if len(groups) >= 2:
                if groups[0].isalpha() and groups[1].isdigit():
                    name = groups[0]
                    val = int(groups[1])
                elif groups[0].isdigit() and groups[1].isalpha():
                    val = int(groups[0])
                    name = groups[1]
                else:
                    name = groups[0]
                    try:
                        val = int(groups[1])
                    except ValueError:
                        val = groups[1]
                return {"Kriya": "Hrasanam", "Karma": name, "Karana": val}

        # Pattern 4: Display (Darshanam)
        match_show = re.search(
            r'(?:(\w+)\s+ko\s+(?:dikhao|darshan|print)|show\s+(\w+)|print\s+(\w+)|(\w+)\s+(?:show|print)\s+karo)',
            line, re.IGNORECASE
        )
        if match_show:
            groups = [g for g in match_show.groups() if g is not None]
            if groups:
                return {"Kriya": "Darshanam", "Karma": groups[0]}

        return None

    def compile_program(self, text):
        lines = text.split("\n")
        program = []
        in_loop = False
        loop_header = None
        loop_sutras = []

        for line_num, line in enumerate(lines, 1):
            line_str = line.strip()
            if not line_str or line_str.startswith(';'):
                continue

            # Detect Loop Start (Pravahanam)
            # Support variables or values as the limit/seema parameter
            match_loop = re.search(
                r'(?:loop\s+chalao\s+jab\s+tak\s+(\w+)\s+((?:"[^"]*")|[\w\d]+)\s+se\s+chota|while\s+(\w+)\s+is\s+less\s+than\s+((?:"[^"]*")|[\w\d]+))',
                line_str, re.IGNORECASE
            )
            if match_loop:
                if in_loop:
                    raise ValueError(f"Line {line_num}: Nested loops not supported in this version.")
                in_loop = True
                groups = [g for g in match_loop.groups() if g is not None]
                limit_val = groups[1]
                try:
                    limit_val = int(limit_val)
                except ValueError:
                    pass
                loop_header = {"var": groups[0], "limit": limit_val}
                continue

            # Detect Loop End
            if in_loop and ("end loop" in line_str.lower() or "loop khatam" in line_str.lower() or "loop_khatam" in line_str.lower()):
                program.append({
                    "Kriya": "Pravahanam",
                    "Adhikarana": loop_header["var"],
                    "Seema": loop_header["limit"],
                    "Sutras": loop_sutras
                })
                in_loop = False
                loop_sutras = []
                continue

            # Standard line compilation
            ast_step = self.compile_line(line_str)
            if ast_step:
                if in_loop:
                    loop_sutras.append(ast_step)
                else:
                    program.append(ast_step)
            else:
                raise SyntaxError(f"Line {line_num}: Invalid syntax. Could not compile: '{line_str}'")

        if in_loop:
            raise SyntaxError("Unterminated loop block at end of file.")

        return program

# Run interactive CLI if executed directly
if __name__ == "__main__":
    from sutralang_vm import SutraVM
    
    compiler = SutraCompiler()
    vm = SutraVM()
    
    print("=" * 60)
    print("      \033[93mSUTRALANG INTERACTIVE VIBE CODING ENVIRONMENT\033[0m")
    print("      Compile conversational Hinglish directly to Sanskrit AST")
    print("=" * 60)
    print("Example Program:")
    print("  ek variable banao counter value 0 rkho")
    print("  loop chalao jab tak counter 3 se chota ho")
    print("    counter ko 1 se badhao")
    print("    counter ko dikhao")
    print("  loop khatam")
    print("-" * 60)
    
    prompt = """
    ek variable banao counter value 0 rkho
    loop chalao jab tak counter 3 se chota ho
      counter ko 1 se badhao
      counter ko dikhao
    loop khatam
    """
    
    print("\033[94mCompiling default test program...\033[0m")
    ast = compiler.compile_program(prompt)
    print(f"\033[32mCompiled Vyakarana AST:\033[0m")
    print(json.dumps(ast, indent=2, ensure_ascii=False))
    print("-" * 60)
    print("\033[94mRunning in SutraVM...\033[0m")
    vm.execute(ast)
