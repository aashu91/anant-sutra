# SutraVM: Sovereign execution engine for Paninian AST
import sys

class SutraVM:
    def __init__(self):
        # The Karta registry stores variable states (Name -> Value)
        self.karta_registry = {}
        # Simple evaluation stack
        self.stack = []

    def log(self, message):
        print(f"[\033[93mSutraVM\033[0m] {message}")

    def execute(self, ast_program):
        self.log("Initializing Sanskrit AST execution...")
        for step in ast_program:
            kriya = step.get("Kriya")
            if not kriya:
                raise ValueError("AST error: Step does not define a 'Kriya' (Action).")
            
            method_name = f"kriya_{kriya.lower()}"
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                method(step)
            else:
                self.log(f"\033[91mError: Unknown Kriya '{kriya}'\033[0m")
                sys.exit(1)
        self.log("Execution completed successfully.")

    # 1. Srujana (सृजन) - Creation of state/variable
    def kriya_srujana(self, step):
        karta = step.get("Karta")
        maan = step.get("Maan", 0)
        if not karta:
            raise ValueError("Kriya Srujana requires a 'Karta' (variable name).")
        self.karta_registry[karta] = maan
        self.log(f"Srujana: Created Karta '{karta}' with Maan = {self.karta_registry[karta]}")

    # 2. Vardhanam (वर्धनम) - Addition / Increment
    def kriya_vardhanam(self, step):
        karma = step.get("Karma")  # Target variable
        karana = step.get("Karana", 1)  # Value to increment by
        
        # Resolve variable if Karana is a Karta name
        val = self.karta_registry.get(karana, karana)
        
        if karma not in self.karta_registry:
            raise KeyError(f"Karma '{karma}' does not exist in registry.")
        
        self.karta_registry[karma] += int(val)
        self.log(f"Vardhanam: Karma '{karma}' increased by {val}. New Maan = {self.karta_registry[karma]}")

    # 3. Hrasanam (ह्रासनम) - Subtraction / Decrement
    def kriya_hrasanam(self, step):
        karma = step.get("Karma")
        karana = step.get("Karana", 1)
        
        val = self.karta_registry.get(karana, karana)
        
        if karma not in self.karta_registry:
            raise KeyError(f"Karma '{karma}' does not exist in registry.")
            
        self.karta_registry[karma] -= int(val)
        self.log(f"Hrasanam: Karma '{karma}' decreased by {val}. New Maan = {self.karta_registry[karma]}")

    # 4. Darshanam (दर्शनम) - Display / Print
    def kriya_darshanam(self, step):
        karma = step.get("Karma")
        if karma in self.karta_registry:
            val = self.karta_registry[karma]
            print(f"\n➔ \033[92m[DARSHANAM OUTPUT]\033[0m {karma} = {val}\n")
        else:
            # Fallback to direct string or literal value
            print(f"\n➔ \033[92m[DARSHANAM OUTPUT]\033[0m {karma}\n")

    # 5. Pravahanam (प्रवाहनम) - Loop / Iteration
    def kriya_pravahanam(self, step):
        # Loop condition variables
        adhikarana = step.get("Adhikarana") # E.g., Loop control criteria
        seema = step.get("Seema") # Limit / Boundary
        sub_ast = step.get("Sutras", []) # Sutras to execute inside loop
        
        if adhikarana not in self.karta_registry:
            raise KeyError(f"Loop controller (Adhikarana) '{adhikarana}' does not exist.")
            
        self.log(f"Pravahanam: Starting loop on '{adhikarana}' up to limit '{seema}'")
        while self.karta_registry[adhikarana] < seema:
            for s_ast in sub_ast:
                # Recursively execute internal sutras
                self.execute([s_ast])

# Simple self-test code when run directly
if __name__ == "__main__":
    test_ast = [
        {"Kriya": "Srujana", "Karta": "tapa_count", "Maan": 0},
        {"Kriya": "Vardhanam", "Karma": "tapa_count", "Karana": 10},
        {"Kriya": "Darshanam", "Karma": "tapa_count"},
        {"Kriya": "Srujana", "Karta": "i", "Maan": 0},
        {
            "Kriya": "Pravahanam",
            "Adhikarana": "i",
            "Seema": 3,
            "Sutras": [
                {"Kriya": "Vardhanam", "Karma": "tapa_count", "Karana": 1},
                {"Kriya": "Vardhanam", "Karma": "i", "Karana": 1},
                {"Kriya": "Darshanam", "Karma": "tapa_count"}
            ]
        }
    ]
    vm = SutraVM()
    vm.execute(test_ast)
