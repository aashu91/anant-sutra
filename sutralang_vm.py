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

    def resolve_value(self, arg):
        if arg in self.karta_registry:
            val = self.karta_registry[arg]
            try:
                return int(val)
            except ValueError:
                return 0
        try:
            return int(arg)
        except ValueError:
            return 0

    def resolve_string(self, arg):
        if arg in self.karta_registry:
            return str(self.karta_registry[arg])
        s = str(arg)
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        return s

    # 1. Srujana (सृजन) - Creation of state/variable
    def kriya_srujana(self, step):
        karta = step.get("Karta")
        maan = step.get("Maan", 0)
        if not karta:
            raise ValueError("Kriya Srujana requires a 'Karta' (variable name).")
        if isinstance(maan, str) and maan in self.karta_registry:
            self.karta_registry[karta] = self.karta_registry[maan]
        else:
            self.karta_registry[karta] = maan
        self.log(f"Srujana: Created Karta '{karta}' with Maan = {self.karta_registry[karta]}")

    # 2. Vardhanam (वर्धनम) - Addition / Increment
    def kriya_vardhanam(self, step):
        karma = step.get("Karma")  # Target variable
        karana = step.get("Karana", 1)  # Value to increment by
        val = self.resolve_value(karana)
        if karma not in self.karta_registry:
            raise KeyError(f"Karma '{karma}' does not exist in registry.")
        self.karta_registry[karma] = self.resolve_value(karma) + val
        self.log(f"Vardhanam: Karma '{karma}' increased by {val}. New Maan = {self.karta_registry[karma]}")

    # 3. Hrasanam (ह्रासनम) - Subtraction / Decrement
    def kriya_hrasanam(self, step):
        karma = step.get("Karma")
        karana = step.get("Karana", 1)
        val = self.resolve_value(karana)
        if karma not in self.karta_registry:
            raise KeyError(f"Karma '{karma}' does not exist in registry.")
        self.karta_registry[karma] = self.resolve_value(karma) - val
        self.log(f"Hrasanam: Karma '{karma}' decreased by {val}. New Maan = {self.karta_registry[karma]}")

    # 4. Darshanam (दर्शनम) - Display / Print
    def kriya_darshanam(self, step):
        karma = step.get("Karma")
        if karma in self.karta_registry:
            val = self.karta_registry[karma]
            print(f"\n➔ \033[92m[DARSHANAM OUTPUT]\033[0m {karma} = {val}\n")
        else:
            s = str(karma)
            if s.startswith('"') and s.endswith('"'):
                s = s[1:-1]
            print(f"\n➔ \033[92m[DARSHANAM OUTPUT]\033[0m {s}\n")

    # 5. Pravahanam (प्रवाहनम) - Loop / Iteration
    def kriya_pravahanam(self, step):
        adhikarana = step.get("Adhikarana")
        seema = step.get("Seema")
        sub_ast = step.get("Sutras", [])
        if adhikarana not in self.karta_registry:
            raise KeyError(f"Loop controller (Adhikarana) '{adhikarana}' does not exist.")
        limit = self.resolve_value(seema)
        self.log(f"Pravahanam: Starting loop on '{adhikarana}' up to limit '{limit}'")
        while self.resolve_value(adhikarana) < limit:
            for s_ast in sub_ast:
                self.execute([s_ast])

    # 6. Yog (Addition)
    def kriya_yog(self, step):
        karta = step.get("Karta")
        val1 = self.resolve_value(step.get("Karana"))
        val2 = self.resolve_value(step.get("Sahakarana"))
        self.karta_registry[karta] = val1 + val2
        self.log(f"Yog: Set '{karta}' to {val1} + {val2} = {self.karta_registry[karta]}")

    # 7. Antar (Subtraction)
    def kriya_antar(self, step):
        karta = step.get("Karta")
        val1 = self.resolve_value(step.get("Karana"))
        val2 = self.resolve_value(step.get("Sahakarana"))
        self.karta_registry[karta] = val1 - val2
        self.log(f"Antar: Set '{karta}' to {val1} - {val2} = {self.karta_registry[karta]}")

    # 8. Gunan (Multiplication)
    def kriya_gunan(self, step):
        karta = step.get("Karta")
        val1 = self.resolve_value(step.get("Karana"))
        val2 = self.resolve_value(step.get("Sahakarana"))
        self.karta_registry[karta] = val1 * val2
        self.log(f"Gunan: Set '{karta}' to {val1} * {val2} = {self.karta_registry[karta]}")

    # 9. Bhagaphalam (Division)
    def kriya_bhagaphalam(self, step):
        karta = step.get("Karta")
        val1 = self.resolve_value(step.get("Karana"))
        val2 = self.resolve_value(step.get("Sahakarana"))
        if val2 == 0:
            raise ZeroDivisionError("Division by zero in Bhagaphalam.")
        self.karta_registry[karta] = val1 // val2
        self.log(f"Bhagaphalam: Set '{karta}' to {val1} / {val2} = {self.karta_registry[karta]}")

    # 10. Sandh (String Join)
    def kriya_sandh(self, step):
        karta = step.get("Karta")
        s1 = self.resolve_string(step.get("Karana"))
        s2 = self.resolve_string(step.get("Sahakarana"))
        self.karta_registry[karta] = s1 + s2
        self.log(f"Sandh: Concatenated \"{s1}\" and \"{s2}\" to set '{karta}' = \"{self.karta_registry[karta]}\"")

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
