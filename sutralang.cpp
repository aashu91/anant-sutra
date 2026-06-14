#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
#include <stdexcept>
#include <regex>
#include <cstdint>

// Termux color outputs
#define COLOR_RESET   "\033[0m"
#define COLOR_YELLOW  "\033[93m"
#define COLOR_GREEN   "\033[92m"
#define COLOR_BLUE    "\033[94m"
#define COLOR_CYAN    "\033[96m"
#define COLOR_RED     "\033[91m"

// Opcode constants
const uint8_t OP_SRUJ = 0x01;
const uint8_t OP_VRDH = 0x02;
const uint8_t OP_HRAS = 0x03;
const uint8_t OP_DRSH = 0x04;
const uint8_t OP_YOG = 0x05;
const uint8_t OP_ANTR = 0x06;
const uint8_t OP_GUN = 0x07;
const uint8_t OP_BHAG = 0x08;
const uint8_t OP_SANDH = 0x09;
const uint8_t OP_SANKALPA = 0x0A;
const uint8_t OP_PRAVAH = 0x0B;
const uint8_t OP_END_BLOCK = 0x0C;
const uint8_t OP_GUNAN = 0x0D;
const uint8_t OP_BHAGAPHALAM = 0x0E;

// Comparison tag constants
const uint8_t COMP_BADA = 0x01;
const uint8_t COMP_CHOTA = 0x02;
const uint8_t COMP_BARABAR = 0x03;

// Value type tags
const uint8_t TAG_INT = 0x01;
const uint8_t TAG_STR = 0x02;
const uint8_t TAG_VAR = 0x03;

// Clean helper to trim whitespace
std::string trim(const std::string& str) {
    size_t first = str.find_first_not_of(" \t\r\n");
    if (std::string::npos == first) {
        return "";
    }
    size_t last = str.find_last_not_of(" \t\r\n");
    return str.substr(first, (last - first + 1));
}

// Upgraded instruction structure
struct Instruction {
    uint8_t opcode = 0;
    std::string karta = "";
    
    struct Value {
        uint8_t type = 0; // TAG_INT, TAG_STR, TAG_VAR
        int int_val = 0;
        std::string str_val = "";
    } op1, op2;
    
    uint8_t sharta_tag = 0; // Used for SANKALPA
    std::vector<Instruction> sub_instructions; // Nested loops/conditionals
};

// Translates conversational vibe prompts (Hinglish/English) to Sanskrit syntax
std::string translate_natural_prompt(const std::string& line) {
    std::string l = trim(line);
    std::string lower_l = l;
    std::transform(lower_l.begin(), lower_l.end(), lower_l.begin(), ::tolower);

    if (lower_l == "loop khatam" || lower_l == "end loop" || lower_l == "loop_khatam" || lower_l == "pravah_khatam") {
        return "pravah_khatam";
    }
    if (lower_l == "sankalpa khatam" || lower_l == "end if" || lower_l == "sankalpa_khatam") {
        return "sankalpa_khatam";
    }

    std::regex create_pat1(R"(ek\s+variable\s+banao\s+(\w+)\s+(?:value|maan)\s+((?:"[^"]*")|[\w\d]+))");
    std::regex create_pat2(R"(create\s+variable\s+(\w+)\s+with\s+(?:value|maan)\s+((?:"[^"]*")|[\w\d]+))");
    std::regex create_pat3(R"(banao\s+variable\s+(\w+)\s+(?:value|maan)\s+((?:"[^"]*")|[\w\d]+))");
    std::regex create_pat4(R"(ek\s+variable\s+(\w+)\s+(?:value|maan)\s+((?:"[^"]*")|[\w\d]+))");
    
    std::smatch match;
    auto orig = [&](int idx) -> std::string {
        return l.substr(match.position(idx), match.length(idx));
    };

    if (std::regex_search(lower_l, match, create_pat1) || 
        std::regex_search(lower_l, match, create_pat2) ||
        std::regex_search(lower_l, match, create_pat3) ||
        std::regex_search(lower_l, match, create_pat4)) {
        return orig(1) + " + sruj(maan=" + orig(2) + ")";
    }

    // Yog (Addition)
    std::regex yog_pat1(R"((\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+aur\s+((?:"[^"]*")|[\w\d]+)\s+ka\s+yog\s+rkho)");
    std::regex yog_pat2(R"(set\s+(\w+)\s+as\s+sum\s+of\s+((?:"[^"]*")|[\w\d]+)\s+and\s+((?:"[^"]*")|[\w\d]+))");
    if (std::regex_search(lower_l, match, yog_pat1) ||
        std::regex_search(lower_l, match, yog_pat2)) {
        return orig(1) + " + yog(karana=" + orig(2) + ", sahakarana=" + orig(3) + ")";
    }

    // Antar (Subtraction)
    std::regex antar_pat1(R"((\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+aur\s+((?:"[^"]*")|[\w\d]+)\s+ka\s+antar\s+rkho)");
    std::regex antar_pat2(R"(set\s+(\w+)\s+as\s+difference\s+of\s+((?:"[^"]*")|[\w\d]+)\s+and\s+((?:"[^"]*")|[\w\d]+))");
    if (std::regex_search(lower_l, match, antar_pat1) ||
        std::regex_search(lower_l, match, antar_pat2)) {
        return orig(1) + " + antar(karana=" + orig(2) + ", sahakarana=" + orig(3) + ")";
    }

    // Gunan (Multiplication)
    std::regex gunan_pat1(R"((\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+aur\s+((?:"[^"]*")|[\w\d]+)\s+ka\s+gunan\s+rkho)");
    std::regex gunan_pat2(R"(set\s+(\w+)\s+as\s+product\s+of\s+((?:"[^"]*")|[\w\d]+)\s+and\s+((?:"[^"]*")|[\w\d]+))");
    if (std::regex_search(lower_l, match, gunan_pat1) ||
        std::regex_search(lower_l, match, gunan_pat2)) {
        return orig(1) + " + gunan(karana=" + orig(2) + ", sahakarana=" + orig(3) + ")";
    }

    // Bhagaphalam (Division)
    std::regex bhagaphalam_pat1(R"((\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+aur\s+((?:"[^"]*")|[\w\d]+)\s+ka\s+bhagaphalam\s+rkho)");
    std::regex bhagaphalam_pat2(R"(set\s+(\w+)\s+as\s+division\s+of\s+((?:"[^"]*")|[\w\d]+)\s+and\s+((?:"[^"]*")|[\w\d]+))");
    if (std::regex_search(lower_l, match, bhagaphalam_pat1) ||
        std::regex_search(lower_l, match, bhagaphalam_pat2)) {
        return orig(1) + " + bhagaphalam(karana=" + orig(2) + ", sahakarana=" + orig(3) + ")";
    }

    // Sandh (String Concatenation)
    std::regex sandh_pat1(R"((\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+aur\s+((?:"[^"]*")|\w+)\s+se\s+jodo)");
    std::regex sandh_pat2(R"((\w+)\s+ko\s+((?:"[^"]*")|\w+)\s+aur\s+((?:"[^"]*")|\w+)\s+ka\s+sandhi\s+rkho)");
    std::regex sandh_pat3(R"(set\s+(\w+)\s+as\s+concatenation\s+of\s+((?:"[^"]*")|\w+)\s+and\s+((?:"[^"]*")|\w+))");
    if (std::regex_search(lower_l, match, sandh_pat1) ||
        std::regex_search(lower_l, match, sandh_pat2) ||
        std::regex_search(lower_l, match, sandh_pat3)) {
        return orig(1) + " + sandh(karana=" + orig(2) + ", sahakarana=" + orig(3) + ")";
    }

    // Vardhanam
    std::regex inc_pat1(R"((\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+se\s+badhao)");
    std::regex inc_pat2(R"(add\s+((?:"[^"]*")|[\w\d]+)\s+to\s+(\w+))");
    std::regex inc_pat3(R"((\w+)\s+me\s+((?:"[^"]*")|[\w\d]+)\s+(?:jod|add))");
    if (std::regex_search(lower_l, match, inc_pat1)) {
        return orig(1) + " + vrdh(karana=" + orig(2) + ")";
    }
    if (std::regex_search(lower_l, match, inc_pat2)) {
        return orig(2) + " + vrdh(karana=" + orig(1) + ")";
    }
    if (std::regex_search(lower_l, match, inc_pat3)) {
        return orig(1) + " + vrdh(karana=" + orig(2) + ")";
    }

    // Hrasanam
    std::regex dec_pat1(R"((\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+se\s+kam\s+karo)");
    std::regex dec_pat2(R"(subtract\s+((?:"[^"]*")|[\w\d]+)\s+from\s+(\w+))");
    std::regex dec_pat3(R"((\w+)\s+se\s+((?:"[^"]*")|[\w\d]+)\s+(?:kam|minus|ghata))");
    if (std::regex_search(lower_l, match, dec_pat1)) {
        return orig(1) + " + hras(karana=" + orig(2) + ")";
    }
    if (std::regex_search(lower_l, match, dec_pat2)) {
        return orig(2) + " + hras(karana=" + orig(1) + ")";
    }
    if (std::regex_search(lower_l, match, dec_pat3)) {
        return orig(1) + " + hras(karana=" + orig(2) + ")";
    }

    // Darshanam
    std::regex show_pat1(R"((.+)\s+ko\s+(?:dikhao|darshan|print))");
    std::regex show_pat2(R"(show\s+(.+))");
    std::regex show_pat3(R"(print\s+(.+))");
    std::regex show_pat4(R"((.+)\s+(?:show|print)\s+karo)");
    if (std::regex_search(lower_l, match, show_pat1) ||
        std::regex_search(lower_l, match, show_pat2) ||
        std::regex_search(lower_l, match, show_pat3) ||
        std::regex_search(lower_l, match, show_pat4)) {
        return orig(1) + " + drsh()";
    }

    // Pravahanam (Loop)
    std::regex loop_pat1(R"(loop\s+chalao\s+jab\s+tak\s+(\w+)\s+((?:"[^"]*")|[\w\d]+)\s+se\s+chota)");
    std::regex loop_pat2(R"(while\s+(\w+)\s+is\s+less\s+than\s+((?:"[^"]*")|[\w\d]+))");
    if (std::regex_search(lower_l, match, loop_pat1) ||
        std::regex_search(lower_l, match, loop_pat2)) {
        return orig(1) + " + pravah(seema=" + orig(2) + ")";
    }

    // Guna (Inline multiply)
    std::regex mult_pat1(R"((\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+se\s+guna\s+karo)");
    std::regex mult_pat2(R"(multiply\s+(\w+)\s+by\s+((?:"[^"]*")|[\w\d]+))");
    if (std::regex_search(lower_l, match, mult_pat1) ||
        std::regex_search(lower_l, match, mult_pat2)) {
        return orig(1) + " + gun(karana=" + orig(2) + ")";
    }

    // Bhaga (Inline divide)
    std::regex div_pat1(R"((\w+)\s+ko\s+((?:"[^"]*")|[\w\d]+)\s+se\s+bhag\s+do)");
    std::regex div_pat2(R"(divide\s+(\w+)\s+by\s+((?:"[^"]*")|[\w\d]+))");
    if (std::regex_search(lower_l, match, div_pat1) ||
        std::regex_search(lower_l, match, div_pat2)) {
        return orig(1) + " + bhag(karana=" + orig(2) + ")";
    }

    // Sankalpa (Conditionals)
    std::regex cond_pat1(R"(agar\s+(\w+)\s+((?:"[^"]*")|[\w\d]+)\s+se\s+bada\s+ho)");
    std::regex cond_pat2(R"(agar\s+(\w+)\s+((?:"[^"]*")|[\w\d]+)\s+se\s+chota\s+ho)");
    std::regex cond_pat3(R"(agar\s+(\w+)\s+((?:"[^"]*")|[\w\d]+)\s+(?:ke\s+barabar|barabar)\s+ho)");
    std::regex cond_pat4(R"(if\s+(\w+)\s+is\s+greater\s+than\s+((?:"[^"]*")|[\w\d]+))");
    std::regex cond_pat5(R"(if\s+(\w+)\s+is\s+less\s+than\s+((?:"[^"]*")|[\w\d]+))");
    std::regex cond_pat6(R"(if\s+(\w+)\s+is\s+equal\s+to\s+((?:"[^"]*")|[\w\d]+))");
    
    if (std::regex_search(lower_l, match, cond_pat1) || std::regex_search(lower_l, match, cond_pat4)) {
        return orig(1) + " + sankalpa(sharta=bada, karana=" + orig(2) + ")";
    }
    if (std::regex_search(lower_l, match, cond_pat2) || std::regex_search(lower_l, match, cond_pat5)) {
        return orig(1) + " + sankalpa(sharta=chota, karana=" + orig(2) + ")";
    }
    if (std::regex_search(lower_l, match, cond_pat3) || std::regex_search(lower_l, match, cond_pat6)) {
        return orig(1) + " + sankalpa(sharta=barabar, karana=" + orig(2) + ")";
    }

    return l; 
}

// Helper to parse operands to Value struct
Instruction::Value parse_value_operand(const std::string& val_str) {
    Instruction::Value val;
    std::string s = trim(val_str);
    if (s.empty()) return val;

    if (s.size() >= 2 && s.front() == '"' && s.back() == '"') {
        val.type = TAG_STR;
        val.str_val = s.substr(1, s.size() - 2);
    } else {
        try {
            size_t idx = 0;
            int num = std::stoi(s, &idx);
            if (idx == s.size()) {
                val.type = TAG_INT;
                val.int_val = num;
            } else {
                val.type = TAG_VAR;
                val.str_val = s;
            }
        } catch (...) {
            val.type = TAG_VAR;
            val.str_val = s;
        }
    }
    return val;
}

// SutraLang Parser (Paninian syntax compiler)
class SutraCompiler {
private:
    void log_err(const std::string& msg, int line_num) {
        std::cerr << COLOR_RED << "[Compiler Error - Line " << line_num << "] " << msg << COLOR_RESET << std::endl;
    }

public:
    Instruction compile_line(std::string line, int line_num) {
        line = trim(line);
        if (line.empty() || line[0] == ';') { // ';' for comments
            return {0, "", {}, {}, 0, {}};
        }

        // Auto-translate if it's natural language vibe prompt (doesn't contain '+')
        if (line.find('+') == std::string::npos && line != "pravah_khatam" && line != "sankalpa_khatam") {
            std::string translated = translate_natural_prompt(line);
            if (translated != line) {
                line = translated;
            } else {
                throw std::runtime_error("Unknown syntax. No Paninian '+' operator, and could not parse as a conversational vibe prompt: '" + line + "'");
            }
        }

        // Check for block terminators
        if (line == "pravah_khatam" || line == "sankalpa_khatam") {
            Instruction inst;
            inst.opcode = OP_END_BLOCK;
            return inst;
        }

        size_t plus_pos = line.find('+');
        if (plus_pos == std::string::npos) {
            throw std::runtime_error("Missing Paninian '+' operator separating Karta and Kriya.");
        }

        std::string karta = trim(line.substr(0, plus_pos));
        std::string right_side = trim(line.substr(plus_pos + 1));

        size_t paren_open = right_side.find('(');
        size_t paren_close = right_side.find(')');

        if (paren_open == std::string::npos || paren_close == std::string::npos || paren_close < paren_open) {
            throw std::runtime_error("Invalid Pratyaya syntax. Expected parenthesis format: 'dhatu(args)'");
        }

        std::string kriya = trim(right_side.substr(0, paren_open));
        std::string args_str = right_side.substr(paren_open + 1, paren_close - paren_open - 1);

        // Parse key=value arguments
        std::unordered_map<std::string, std::string> args;
        std::stringstream ss(args_str);
        std::string item;
        while (std::getline(ss, item, ',')) {
            item = trim(item);
            if (item.empty()) continue;
            size_t eq_pos = item.find('=');
            if (eq_pos == std::string::npos) {
                throw std::runtime_error("Arguments must be specified as key=value pairings.");
            }
            std::string key = trim(item.substr(0, eq_pos));
            std::string val = trim(item.substr(eq_pos + 1));
            args[key] = val;
        }

        Instruction inst;
        inst.karta = karta;
        
        std::transform(kriya.begin(), kriya.end(), kriya.begin(), ::tolower);
        if (kriya == "sruj") {
            inst.opcode = OP_SRUJ;
            inst.op1 = parse_value_operand(args["maan"]);
        } else if (kriya == "vrdh") {
            inst.opcode = OP_VRDH;
            inst.op1 = parse_value_operand(args["karana"]);
        } else if (kriya == "hras") {
            inst.opcode = OP_HRAS;
            inst.op1 = parse_value_operand(args["karana"]);
        } else if (kriya == "drsh") {
            inst.opcode = OP_DRSH;
            inst.op1 = parse_value_operand(karta); // Print value of karta
        } else if (kriya == "yog") {
            inst.opcode = OP_YOG;
            inst.op1 = parse_value_operand(args["karana"]);
            inst.op2 = parse_value_operand(args["sahakarana"]);
        } else if (kriya == "antar") {
            inst.opcode = OP_ANTR;
            inst.op1 = parse_value_operand(args["karana"]);
            inst.op2 = parse_value_operand(args["sahakarana"]);
        } else if (kriya == "gunan") {
            inst.opcode = OP_GUNAN;
            inst.op1 = parse_value_operand(args["karana"]);
            inst.op2 = parse_value_operand(args["sahakarana"]);
        } else if (kriya == "bhagaphalam") {
            inst.opcode = OP_BHAGAPHALAM;
            inst.op1 = parse_value_operand(args["karana"]);
            inst.op2 = parse_value_operand(args["sahakarana"]);
        } else if (kriya == "gun") {
            inst.opcode = OP_GUN;
            inst.op1 = parse_value_operand(args["karana"]);
        } else if (kriya == "bhag") {
            inst.opcode = OP_BHAG;
            inst.op1 = parse_value_operand(args["karana"]);
        } else if (kriya == "sandh") {
            inst.opcode = OP_SANDH;
            inst.op1 = parse_value_operand(args["karana"]);
            inst.op2 = parse_value_operand(args["sahakarana"]);
        } else if (kriya == "sankalpa") {
            inst.opcode = OP_SANKALPA;
            std::string sharta = args["sharta"];
            if (sharta == "bada") inst.sharta_tag = COMP_BADA;
            else if (sharta == "chota") inst.sharta_tag = COMP_CHOTA;
            else inst.sharta_tag = COMP_BARABAR;
            inst.op1 = parse_value_operand(args["karana"]);
        } else if (kriya == "pravah") {
            inst.opcode = OP_PRAVAH;
            inst.op1 = parse_value_operand(args["seema"]);
        } else {
            throw std::runtime_error("Unknown Dhatu action: '" + kriya + "'");
        }

        return inst;
    }

    std::vector<Instruction> compile_program(const std::string& filepath) {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            throw std::runtime_error("Could not open source file: " + filepath);
        }

        std::vector<Instruction> program;
        std::vector<Instruction*> loop_stack;
        std::string line;
        int line_num = 0;

        while (std::getline(file, line)) {
            line_num++;
            try {
                Instruction inst = compile_line(line, line_num);
                if (inst.opcode == 0) continue; // Skip comments/empty lines

                if (inst.opcode == OP_END_BLOCK) {
                    if (loop_stack.empty()) {
                        throw std::runtime_error("Orphan block end without matching block start.");
                    }
                    loop_stack.pop_back();
                } else if (inst.opcode == OP_PRAVAH || inst.opcode == OP_SANKALPA) {
                    if (loop_stack.empty()) {
                        program.push_back(inst);
                        loop_stack.push_back(&program.back());
                    } else {
                        loop_stack.back()->sub_instructions.push_back(inst);
                        loop_stack.push_back(&(loop_stack.back()->sub_instructions.back()));
                    }
                } else {
                    if (loop_stack.empty()) {
                        program.push_back(inst);
                    } else {
                        loop_stack.back()->sub_instructions.push_back(inst);
                    }
                }
            } catch (const std::exception& e) {
                log_err(e.what(), line_num);
                file.close();
                exit(1);
            }
        }
        file.close();

        if (!loop_stack.empty()) {
            std::cerr << COLOR_RED << "Compilation Error: Unterminated loop/conditional block at end of file." << COLOR_RESET << std::endl;
            exit(1);
        }

        return program;
    }
};

// Variable type supporting either int or string
struct Variable {
    bool is_string = false;
    int int_val = 0;
    std::string str_val = "";
};

// SutraVM: Execution runtime for compiled instructions
class SutraVM {
private:
    std::unordered_map<std::string, Variable> karta_registry;

    void log(const std::string& msg) {
        std::cout << COLOR_YELLOW << "[SutraVM] " << COLOR_RESET << msg << std::endl;
    }

    int resolve_value(const Instruction::Value& op) {
        if (op.type == TAG_INT) {
            return op.int_val;
        }
        if (op.type == TAG_VAR) {
            std::string var_name = op.str_val;
            if (karta_registry.find(var_name) != karta_registry.end()) {
                if (karta_registry[var_name].is_string) {
                    try {
                        return std::stoi(karta_registry[var_name].str_val);
                    } catch (...) {
                        return 0;
                    }
                }
                return karta_registry[var_name].int_val;
            }
            return 0;
        }
        // TAG_STR
        try {
            return std::stoi(op.str_val);
        } catch (...) {
            return 0;
        }
    }

    std::string resolve_string(const Instruction::Value& op) {
        if (op.type == TAG_STR) {
            return op.str_val;
        }
        if (op.type == TAG_VAR) {
            std::string var_name = op.str_val;
            if (karta_registry.find(var_name) != karta_registry.end()) {
                if (karta_registry[var_name].is_string) {
                    return karta_registry[var_name].str_val;
                }
                return std::to_string(karta_registry[var_name].int_val);
            }
            return "";
        }
        // TAG_INT
        return std::to_string(op.int_val);
    }

public:
    void execute(const std::vector<Instruction>& program) {
        for (const auto& inst : program) {
            if (inst.opcode == OP_SRUJ) { // Srujana
                Variable var;
                if (inst.op1.type == TAG_INT) {
                    var.int_val = inst.op1.int_val;
                } else if (inst.op1.type == TAG_STR) {
                    var.is_string = true;
                    var.str_val = inst.op1.str_val;
                } else { // TAG_VAR
                    if (karta_registry.find(inst.op1.str_val) != karta_registry.end()) {
                        var = karta_registry[inst.op1.str_val];
                    } else {
                        var.is_string = true;
                        var.str_val = inst.op1.str_val;
                    }
                }
                karta_registry[inst.karta] = var;
                if (var.is_string) {
                    log("Srujana: Created variable '" + inst.karta + "' with Maan = \"" + var.str_val + "\"");
                } else {
                    log("Srujana: Created variable '" + inst.karta + "' with Maan = " + std::to_string(var.int_val));
                }
            }
            else if (inst.opcode == OP_VRDH) { // Vardhanam
                if (karta_registry.find(inst.karta) == karta_registry.end()) {
                    throw std::runtime_error("Variable '" + inst.karta + "' not declared before Vardhanam.");
                }
                int add_val = resolve_value(inst.op1);
                karta_registry[inst.karta].int_val += add_val;
                log("Vardhanam: '" + inst.karta + "' increased by " + std::to_string(add_val) + ". New Maan = " + std::to_string(karta_registry[inst.karta].int_val));
            }
            else if (inst.opcode == OP_HRAS) { // Hrasanam
                if (karta_registry.find(inst.karta) == karta_registry.end()) {
                    throw std::runtime_error("Variable '" + inst.karta + "' not declared before Hrasanam.");
                }
                int sub_val = resolve_value(inst.op1);
                karta_registry[inst.karta].int_val -= sub_val;
                log("Hrasanam: '" + inst.karta + "' decreased by " + std::to_string(sub_val) + ". New Maan = " + std::to_string(karta_registry[inst.karta].int_val));
            }
            else if (inst.opcode == OP_DRSH) { // Darshanam
                std::string val_str = resolve_string(inst.op1);
                std::cout << COLOR_GREEN << "➔ [DARSHANAM] " << val_str << COLOR_RESET << std::endl;
            }
            else if (inst.opcode == OP_GUN) { // Guna (inline multiply)
                if (karta_registry.find(inst.karta) == karta_registry.end()) {
                    throw std::runtime_error("Variable '" + inst.karta + "' not declared before Guna.");
                }
                int mult_val = resolve_value(inst.op1);
                karta_registry[inst.karta].int_val *= mult_val;
                log("Guna: '" + inst.karta + "' multiplied by " + std::to_string(mult_val) + ". New Maan = " + std::to_string(karta_registry[inst.karta].int_val));
            }
            else if (inst.opcode == OP_BHAG) { // Bhaga (inline divide)
                if (karta_registry.find(inst.karta) == karta_registry.end()) {
                    throw std::runtime_error("Variable '" + inst.karta + "' not declared before Bhaga.");
                }
                int div_val = resolve_value(inst.op1);
                if (div_val == 0) {
                    throw std::runtime_error("Mathematical error: Division by zero is not allowed.");
                }
                karta_registry[inst.karta].int_val /= div_val;
                log("Bhaga: '" + inst.karta + "' divided by " + std::to_string(div_val) + ". New Maan = " + std::to_string(karta_registry[inst.karta].int_val));
            }
            else if (inst.opcode == OP_YOG) { // Yog
                Variable var;
                int val1 = resolve_value(inst.op1);
                int val2 = resolve_value(inst.op2);
                var.int_val = val1 + val2;
                karta_registry[inst.karta] = var;
                log("Yog: Set '" + inst.karta + "' to " + std::to_string(val1) + " + " + std::to_string(val2) + " = " + std::to_string(var.int_val));
            }
            else if (inst.opcode == OP_ANTR) { // Antar
                Variable var;
                int val1 = resolve_value(inst.op1);
                int val2 = resolve_value(inst.op2);
                var.int_val = val1 - val2;
                karta_registry[inst.karta] = var;
                log("Antar: Set '" + inst.karta + "' to " + std::to_string(val1) + " - " + std::to_string(val2) + " = " + std::to_string(var.int_val));
            }
            else if (inst.opcode == OP_GUNAN) { // Gunan
                Variable var;
                int val1 = resolve_value(inst.op1);
                int val2 = resolve_value(inst.op2);
                var.int_val = val1 * val2;
                karta_registry[inst.karta] = var;
                log("Gunan: Set '" + inst.karta + "' to " + std::to_string(val1) + " * " + std::to_string(val2) + " = " + std::to_string(var.int_val));
            }
            else if (inst.opcode == OP_BHAGAPHALAM) { // Bhagaphalam
                Variable var;
                int val1 = resolve_value(inst.op1);
                int val2 = resolve_value(inst.op2);
                if (val2 == 0) {
                    throw std::runtime_error("Mathematical error: Division by zero in Bhagaphalam.");
                }
                var.int_val = val1 / val2;
                karta_registry[inst.karta] = var;
                log("Bhagaphalam: Set '" + inst.karta + "' to " + std::to_string(val1) + " / " + std::to_string(val2) + " = " + std::to_string(var.int_val));
            }
            else if (inst.opcode == OP_SANDH) { // Sandh
                Variable var;
                var.is_string = true;
                std::string s1 = resolve_string(inst.op1);
                std::string s2 = resolve_string(inst.op2);
                var.str_val = s1 + s2;
                karta_registry[inst.karta] = var;
                log("Sandh: Concatenated \"" + s1 + "\" and \"" + s2 + "\" to set '" + inst.karta + "' = \"" + var.str_val + "\"");
            }
            else if (inst.opcode == OP_SANKALPA) { // Sankalpa
                if (karta_registry.find(inst.karta) == karta_registry.end()) {
                    throw std::runtime_error("Condition variable '" + inst.karta + "' not declared before Sankalpa.");
                }
                int val = resolve_value({TAG_VAR, 0, inst.karta});
                int comp = resolve_value(inst.op1);
                bool condition_met = false;
                
                if (inst.sharta_tag == COMP_BADA) condition_met = (val > comp);
                else if (inst.sharta_tag == COMP_CHOTA) condition_met = (val < comp);
                else if (inst.sharta_tag == COMP_BARABAR) condition_met = (val == comp);
                
                if (condition_met) {
                    execute(inst.sub_instructions);
                }
            }
            else if (inst.opcode == OP_PRAVAH) { // Pravahanam
                if (karta_registry.find(inst.karta) == karta_registry.end()) {
                    throw std::runtime_error("Loop variable '" + inst.karta + "' not declared before Pravahanam.");
                }
                log("Pravahanam: Starting loop on '" + inst.karta + "'");
                while (resolve_value({TAG_VAR, 0, inst.karta}) < resolve_value(inst.op1)) {
                    execute(inst.sub_instructions);
                }
                log("Pravahanam: Loop ended.");
            }
        }
    }
};

// Bytecode Reader
std::vector<Instruction> read_bytecode(std::istream& in) {
    std::vector<Instruction> program;
    std::vector<Instruction*> block_stack;
    
    while (in.peek() != EOF) {
        uint8_t opcode = 0;
        in.read(reinterpret_cast<char*>(&opcode), 1);
        if (in.gcount() == 0) break;
        
        Instruction inst;
        inst.opcode = opcode;
        
        if (opcode == OP_END_BLOCK) {
            if (block_stack.empty()) {
                throw std::runtime_error("Orphan END_BLOCK opcode in bytecode.");
            }
            block_stack.pop_back();
            continue;
        }
        
        auto read_ident = [&]() -> std::string {
            uint16_t len = 0;
            in.read(reinterpret_cast<char*>(&len), 2);
            std::string s(len, '\0');
            in.read(&s[0], len);
            return s;
        };
        
        auto read_value = [&]() -> Instruction::Value {
            Instruction::Value val;
            in.read(reinterpret_cast<char*>(&val.type), 1);
            if (val.type == TAG_INT) {
                in.read(reinterpret_cast<char*>(&val.int_val), 4);
            } else {
                uint16_t len = 0;
                in.read(reinterpret_cast<char*>(&len), 2);
                val.str_val.resize(len);
                in.read(&val.str_val[0], len);
            }
            return val;
        };
        
        if (opcode == OP_SRUJ || opcode == OP_VRDH || opcode == OP_HRAS || opcode == OP_GUN || opcode == OP_BHAG) {
            inst.karta = read_ident();
            inst.op1 = read_value();
        } else if (opcode == OP_DRSH) {
            inst.op1 = read_value();
        } else if (opcode == OP_YOG || opcode == OP_ANTR || opcode == OP_GUNAN || opcode == OP_BHAGAPHALAM || opcode == OP_SANDH) {
            inst.karta = read_ident();
            inst.op1 = read_value();
            inst.op2 = read_value();
        } else if (opcode == OP_SANKALPA) {
            inst.karta = read_ident();
            in.read(reinterpret_cast<char*>(&inst.sharta_tag), 1);
            inst.op1 = read_value();
        } else if (opcode == OP_PRAVAH) {
            inst.karta = read_ident();
            inst.op1 = read_value();
        } else {
            throw std::runtime_error("Unknown opcode in bytecode: " + std::to_string(opcode));
        }
        
        if (opcode == OP_PRAVAH || opcode == OP_SANKALPA) {
            if (block_stack.empty()) {
                program.push_back(inst);
                block_stack.push_back(&program.back());
            } else {
                block_stack.back()->sub_instructions.push_back(inst);
                block_stack.push_back(&(block_stack.back()->sub_instructions.back()));
            }
        } else {
            if (block_stack.empty()) {
                program.push_back(inst);
            } else {
                block_stack.back()->sub_instructions.push_back(inst);
            }
        }
    }
    
    if (!block_stack.empty()) {
        throw std::runtime_error("Unterminated block(s) in bytecode.");
    }
    
    return program;
}

// Bytecode Writer / Serialization helpers
void write_value(std::ostream& out, const Instruction::Value& val) {
    out.write(reinterpret_cast<const char*>(&val.type), 1);
    if (val.type == TAG_INT) {
        out.write(reinterpret_cast<const char*>(&val.int_val), 4);
    } else {
        uint16_t len = val.str_val.size();
        out.write(reinterpret_cast<const char*>(&len), 2);
        out.write(val.str_val.data(), len);
    }
}

void write_ident(std::ostream& out, const std::string& ident) {
    uint16_t len = ident.size();
    out.write(reinterpret_cast<const char*>(&len), 2);
    out.write(ident.data(), len);
}

void write_instruction(std::ostream& out, const Instruction& inst) {
    out.write(reinterpret_cast<const char*>(&inst.opcode), 1);
    
    if (inst.opcode == OP_SRUJ || inst.opcode == OP_VRDH || inst.opcode == OP_HRAS || inst.opcode == OP_GUN || inst.opcode == OP_BHAG) {
        write_ident(out, inst.karta);
        write_value(out, inst.op1);
    } else if (inst.opcode == OP_DRSH) {
        write_value(out, inst.op1);
    } else if (inst.opcode == OP_YOG || inst.opcode == OP_ANTR || inst.opcode == OP_GUNAN || inst.opcode == OP_BHAGAPHALAM || inst.opcode == OP_SANDH) {
        write_ident(out, inst.karta);
        write_value(out, inst.op1);
        write_value(out, inst.op2);
    } else if (inst.opcode == OP_SANKALPA) {
        write_ident(out, inst.karta);
        out.write(reinterpret_cast<const char*>(&inst.sharta_tag), 1);
        write_value(out, inst.op1);
    } else if (inst.opcode == OP_PRAVAH) {
        write_ident(out, inst.karta);
        write_value(out, inst.op1);
    }
    
    if (inst.opcode == OP_PRAVAH || inst.opcode == OP_SANKALPA) {
        for (const auto& sub : inst.sub_instructions) {
            write_instruction(out, sub);
        }
        uint8_t end_op = OP_END_BLOCK;
        out.write(reinterpret_cast<const char*>(&end_op), 1);
    }
}

void save_program_to_bytecode(const std::vector<Instruction>& program, const std::string& filepath) {
    std::ofstream out(filepath, std::ios::binary);
    if (!out.is_open()) {
        throw std::runtime_error("Could not write bytecode file: " + filepath);
    }
    out.write("SUTR", 4);
    uint8_t version = 1;
    out.write(reinterpret_cast<const char*>(&version), 1);
    for (const auto& inst : program) {
        write_instruction(out, inst);
    }
    out.close();
}

int main(int argc, char* argv[]) {
    std::cout << COLOR_CYAN << "==========================================" << COLOR_RESET << std::endl;
    std::cout << COLOR_CYAN << "  SUTRA: Pure Paninian C++ Compiler/VM   " << COLOR_RESET << std::endl;
    std::cout << COLOR_CYAN << "==========================================" << COLOR_RESET << std::endl;

    if (argc < 2) {
        std::cout << "Usage: ./sutra <filename.sutra | filename.sutrab>" << std::endl;
        return 1;
    }

    std::string filename = argv[1];
    
    // Check if binary or text
    std::ifstream check_file(filename, std::ios::binary);
    if (!check_file.is_open()) {
        std::cerr << COLOR_RED << "Error: Could not open file: " << filename << COLOR_RESET << std::endl;
        return 1;
    }
    
    char magic[4] = {0};
    check_file.read(magic, 4);
    bool is_binary = (std::string(magic, 4) == "SUTR");
    check_file.close();
    
    std::vector<Instruction> program;
    
    if (is_binary) {
        std::cout << COLOR_BLUE << "[VM] Loading binary bytecode file..." << COLOR_RESET << std::endl;
        std::ifstream in(filename, std::ios::binary);
        // Skip header (5 bytes)
        in.seekg(5);
        try {
            program = read_bytecode(in);
        } catch (const std::exception& e) {
            std::cerr << COLOR_RED << "Bytecode Load Error: " << e.what() << COLOR_RESET << std::endl;
            in.close();
            return 1;
        }
        in.close();
    } else {
        std::cout << COLOR_BLUE << "[Compiler] Compiling source file to bytecode..." << COLOR_RESET << std::endl;
        SutraCompiler compiler;
        try {
            program = compiler.compile_program(filename);
            
            // Save bytecode to filename + "b" (e.g. test.sutra -> test.sutrab)
            std::string out_filename = filename + "b";
            save_program_to_bytecode(program, out_filename);
            std::cout << COLOR_GREEN << "[Compiler] Bytecode successfully generated & written to: " << out_filename << COLOR_RESET << std::endl;
        } catch (const std::exception& e) {
            std::cerr << COLOR_RED << "Compilation Failed: " << e.what() << COLOR_RESET << std::endl;
            return 1;
        }
    }
    
    std::cout << COLOR_BLUE << "[VM] Executing program instructions..." << COLOR_RESET << std::endl;
    SutraVM vm;
    try {
        vm.execute(program);
    } catch (const std::exception& e) {
        std::cerr << COLOR_RED << "Execution Runtime Error: " << e.what() << COLOR_RESET << std::endl;
        return 1;
    }
    
    std::cout << COLOR_GREEN << "[VM] Execution finished successfully." << COLOR_RESET << std::endl;
    return 0;
}
