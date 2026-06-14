# SutraLang Compiler: Translates Hinglish/English Vibe Prompts to Paninian AST
import re
import json

class SutraCompiler:
    def __init__(self):
        pass

    def log(self, message):
        print(f"[\033[96mSutraCompiler\033[0m] {message}")

    def compile_line(self, line):
        line = line.strip().lower()
        if not line:
            return None

        # Pattern 1: Variable Creation (Srujana)
        # Examples: "ek variable banao jiska naam counter ho aur value 0 ho"
        # "create variable score with value 10"
        # "x variable banao value 5 rkho"
        match_create = re.search(
            r'(?:variable\s+(\w+)\s+banao|ek\s+variable\s+banao\s+jiska\s+naam\s+(\w+)\s+ho|create\s+variable\s+(\w+)|ek\s+variable\s+banao\s+(\w+))'
            r'.*?(?:value|maan)\s+(\d+)', 
            line
        ) or re.search(
            r'(?:banao|create)\s+variable\s+(\w+)\s+with\s+(?:value|maan)\s+(\d+)',
            line
        )
        if match_create:
            # Extract variable name and value
            groups = [g for g in match_create.groups() if g is not None]
            if len(groups) >= 2:
                name = groups[0]
                val = int(groups[1])
                return {"Kriya": "Srujana", "Karta": name, "Maan": val}

        # Pattern 2: Increment (Vardhanam)
        # Examples: "counter ko 1 se badhao", "add 5 to score", "x me 2 jod do"
        match_inc = re.search(
            r'(?:(\w+)\s+ko\s+(\d+)\s+se\s+badhao|add\s+(\d+)\s+to\s+(\w+)|(\w+)\s+me\s+(\d+)\s+(?:jod|add))',
            line
        )
        if match_inc:
            groups = [g for g in match_inc.groups() if g is not None]
            if len(groups) >= 2:
                # Determine which group is variable and which is value
                # Case 1: counter (group 0), 1 (group 1)
                if groups[0].isalpha() and groups[1].isdigit():
                    name = groups[0]
                    val = int(groups[1])
                # Case 2: 5 (group 0), score (group 1)
                elif groups[0].isdigit() and groups[1].isalpha():
                    val = int(groups[0])
                    name = groups[1]
                else:
                    name = groups[0]
                    val = int(groups[1])
                return {"Kriya": "Vardhanam", "Karma": name, "Karana": val}

        # Pattern 3: Decrement (Hrasanam)
        # Examples: "counter ko 1 se kam karo", "subtract 2 from x", "score se 5 ghata do"
        match_dec = re.search(
            r'(?:(\w+)\s+ko\s+(\d+)\s+se\s+kam\s+karo|subtract\s+(\d+)\s+from\s+(\w+)|(\w+)\s+se\s+(\d+)\s+(?:kam|minus|ghata))',
            line
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
                    val = int(groups[1])
                return {"Kriya": "Hrasanam", "Karma": name, "Karana": val}

        # Pattern 4: Display (Darshanam)
        # Examples: "counter ko dikhao", "print score", "x show karo"
        match_show = re.search(
            r'(?:(\w+)\s+ko\s+(?:dikhao|darshan|print)|show\s+(\w+)|print\s+(\w+)|(\w+)\s+(?:show|print)\s+karo)',
            line
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

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Detect Loop Start (Pravahanam)
            # Examples: "loop chalao jab tak i 5 se chota ho"
            # "loop: i up to 3"
            match_loop = re.search(
                r'(?:loop\s+chalao\s+jab\s+tak\s+(\w+)\s+(\d+)\s+se\s+chota|while\s+(\w+)\s+is\s+less\s+than\s+(\d+))',
                line_str.lower()
            )
            if match_loop:
                in_loop = True
                groups = [g for g in match_loop.groups() if g is not None]
                loop_header = {"var": groups[0], "limit": int(groups[1])}
                continue

            # Detect Loop End
            if in_loop and ("end loop" in line_str.lower() or "loop khatam" in line_str.lower()):
                # Construct Pravahanam Kriya
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
                self.log(f"\033[93mSkipped line (could not parse): '{line_str}'\033[0m")

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
