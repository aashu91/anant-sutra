# SutraLang Neuro-Symbolic Compiler
# Translates complex free-form natural prompts to formal SutraLang code using local Ollama model

import urllib.request
import json
import sys
import re
from sutralang_compiler import SutraCompiler

MODEL_NAME = "hf.co/bartowski/gemma-2-2b-it-abliterated-GGUF:Q4_K_M"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT = """You are the SutraLang Semantic Compiler. Your task is to translate free-form natural language programming requests into formal SutraLang statements.

SutraLang syntax rules (strictly follow this syntax):
1. Variable creation:
   ek variable [name] value [val]
   (val can be a number like 10 or double-quoted string like "Ashutosh")
2. Add value to variable:
   [name] ko [val] se badhao
   [name] me [val] jod do
3. Subtract value:
   [name] ko [val] se kam karo
   [name] se [val] ghata do
4. Display/Print:
   [name] ko dikhao
   print [name]
5. Complex math operations:
   [name] ko [val1] aur [val2] ka yog rkho
   [name] ko [val1] aur [val2] ka antar rkho
   [name] ko [val1] aur [val2] ka gunan rkho
   [name] ko [val1] aur [val2] ka bhagaphalam rkho
6. String joining:
   [name] ko [val1] aur [val2] se jodo
7. Conditionals:
   agar [var] [comp] se bada ho
   agar [var] [comp] se chota ho
   agar [var] [comp] ke barabar ho
   sankalpa khatam
8. Loops:
   loop chalao jab tak [var] [limit] se chota
   loop_khatam

Do NOT use any semicolons, brackets [], standard arithmetic symbols (+, -, *, /) or other non-documented syntax. Use only lowercase variable names.

Examples:

Input: Create a name variable with value "Aashu" and print it.
Output:
ek variable name value "Aashu"
print name

Input: Create a counter starting at 0, loop 3 times, inside the loop add 1 to the counter and print the counter.
Output:
ek variable counter value 0
ek variable limit value 3
ek variable i value 0
loop chalao jab tak i limit se chota
  counter ko 1 se badhao
  print counter
  i ko 1 se badhao
loop_khatam

Input: Join name "Ashutosh" and surname "Singh" with a space and print it.
Output:
ek variable name value "Ashutosh"
ek variable surname value "Singh"
ek variable space value " "
ek variable temp value ""
temp ko name aur space se jodo
ek variable full_name value ""
full_name ko temp aur surname se jodo
print full_name

Input: Define num as 10. If num equals 10, print "Success".
Output:
ek variable num value 10
agar num 10 ke barabar ho
  print "Success"
sankalpa khatam

Output ONLY the formal SutraLang statements, one per line. Do not include any explanations, markdown code blocks, comments, or extra text."""

def query_ollama(prompt):
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }
    req = urllib.request.Request(OLLAMA_API_URL)
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req, json.dumps(data).encode('utf-8'))
        res_data = json.loads(response.read().decode('utf-8'))
        return res_data.get("response", "").strip()
    except Exception as e:
        print(f"\033[91mError calling Ollama API: {e}\033[0m")
        sys.exit(1)

def self_correct(failing_line, error_msg):
    correction_prompt = f"The following line has a syntax error: '{failing_line}'.\nError: {error_msg}\nRewrite this line so it strictly conforms to SutraLang syntax rules. Output ONLY the corrected line."
    print(f"\033[93m[Self-Correction] Correcting line: '{failing_line}'...\033[0m")
    corrected = query_ollama(correction_prompt)
    # Strip any markdown backticks if returned
    corrected = re.sub(r'[`\n\r]', '', corrected).strip()
    return corrected

def compile_neuro_prompt(prompt):
    print(f"\033[94m[Neuro-Symbolic] Querying local LLM for translation...\033[0m")
    raw_output = query_ollama(prompt)
    
    # Process lines
    lines = [line.strip() for line in raw_output.split('\n') if line.strip()]
    cleaned_lines = []
    
    for line in lines:
        # Strip markdown code blocks if the model wrapped output
        if line.startswith("```") or line.endswith("```"):
            continue
        cleaned_lines.append(line)
        
    compiler = SutraCompiler()
    verified_ast = []
    
    print(f"\033[92m[Semantic Compilation Output]\033[0m")
    for line in cleaned_lines:
        print(f"  {line}")
        
    print(f"\n\033[94m[Neuro-Symbolic] Validating code logic via compiler...\033[0m")
    
    # Compile the entire program text with block-level symbolic validation
    program_text = "\n".join(cleaned_lines)
    attempts = 0
    verified_ast = None
    
    while attempts < 3:
        try:
            verified_ast = compiler.compile_program(program_text)
            break
        except Exception as e:
            print(f"\033[91mSyntax Validation Error: {e}\033[0m")
            attempts += 1
            if attempts == 3:
                print(f"\033[91mFailed to compile program after 3 self-correction attempts.\033[0m")
                sys.exit(1)
            
            # Feed the invalid code and exact compiler error back to local model to self-correct
            correction_prompt = (
                f"Your previous code generation has a compilation error.\n"
                f"Code:\n---\n{program_text}\n---\n"
                f"Error: {e}\n\n"
                f"Please rewrite the entire program code so it strictly conforms to SutraLang syntax rules.\n"
                f"Output ONLY the corrected code lines. Do not output any markdown fences, comments, or extra text."
            )
            print(f"\033[93m[Self-Correction] Attempt {attempts}: Requesting LLM to correct the syntax...\033[0m")
            program_text = query_ollama(correction_prompt)
            # Clean up output
            lines = [line.strip() for line in program_text.split('\n') if line.strip()]
            cleaned_lines = []
            for line in lines:
                if line.startswith("```") or line.endswith("```"):
                    continue
                cleaned_lines.append(line)
            program_text = "\n".join(cleaned_lines)
            
            print(f"\033[92m[Corrected Output]\033[0m")
            for line in cleaned_lines:
                print(f"  {line}")

    print(f"\033[92m[Verification] Program successfully validated and compiled to AST!\033[0m")
    return verified_ast

if __name__ == "__main__":
    if len(sys.argv) < 2:
        test_prompt = "Create a name variable with value 'Aashu' and print it, then create a counter starting at 0, loop 3 times, inside the loop add 1 to the counter and print the counter."
        print(f"No prompt provided. Running default neuro-symbolic test: '{test_prompt}'\n")
    else:
        test_prompt = sys.argv[1]
        
    ast = compile_neuro_prompt(test_prompt)
    
    # Execute the AST on VM
    from sutralang_vm import SutraVM
    vm = SutraVM()
    vm.execute(ast)
