#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
#include <stdexcept>
#include <regex>

// Termux color outputs
#define COLOR_RESET   "\033[0m"
#define COLOR_YELLOW  "\033[93m"
#define COLOR_GREEN   "\033[92m"
#define COLOR_BLUE    "\033[94m"
#define COLOR_CYAN    "\033[96m"
#define COLOR_RED     "\033[91m"

// Vyakarana Instruction representation
struct Instruction {
    std::string kriya; // Dhatu name (sruj, vrdh, hras, drsh, pravah)
    std::string karta; // Primary state/variable (left-hand side)
    std::unordered_map<std::string, std::string> args; // Parameters inside pratyaya (e.g., maan=0)
    std::vector<Instruction> sub_instructions; // Nested loop instructions
};

// Clean helper to trim whitespace
std::string trim(const std::string& str) {
    size_t first = str.find_first_not_of(" \t\r\n");
    if (std::string::npos == first) {
        return "";
    }
    size_t last = str.find_last_not_of(" \t\r\n");
    return str.substr(first, (last - first + 1));
}

// Translates conversational vibe prompts (Hinglish/English) to Sanskrit syntax
std::string translate_natural_prompt(const std::string& line) {
    std::string l = trim(line);
    std::string lower_l = l;
    std::transform(lower_l.begin(), lower_l.end(), lower_l.begin(), ::tolower);

    if (lower_l == "loop khatam" || lower_l == "end loop" || lower_l == "loop_khatam") {
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
    std::regex yog_pat1(R"((\w+)\s+ko\s+(\w+)\s+aur\s+(\w+)\s+ka\s+yog\s+rkho)");
    std::regex yog_pat2(R"(set\s+(\w+)\s+as\s+sum\s+of\s+(\w+)\s+and\s+(\w+))");
    if (std::regex_search(lower_l, match, yog_pat1) ||
        std::regex_search(lower_l, match, yog_pat2)) {
        return orig(1) + " + yog(karana=" + orig(2) + ", sahakarana=" + orig(3) + ")";
    }

    // Antar (Subtraction)
    std::regex antar_pat1(R"((\w+)\s+ko\s+(\w+)\s+aur\s+(\w+)\s+ka\s+antar\s+rkho)");
    std::regex antar_pat2(R"(set\s+(\w+)\s+as\s+difference\s+of\s+(\w+)\s+and\s+(\w+))");
    if (std::regex_search(lower_l, match, antar_pat1) ||
        std::regex_search(lower_l, match, antar_pat2)) {
        return orig(1) + " + antar(karana=" + orig(2) + ", sahakarana=" + orig(3) + ")";
    }

    // Gunan (Multiplication)
    std::regex gunan_pat1(R"((\w+)\s+ko\s+(\w+)\s+aur\s+(\w+)\s+ka\s+gunan\s+rkho)");
    std::regex gunan_pat2(R"(set\s+(\w+)\s+as\s+product\s+of\s+(\w+)\s+and\s+(\w+))");
    if (std::regex_search(lower_l, match, gunan_pat1) ||
        std::regex_search(lower_l, match, gunan_pat2)) {
        return orig(1) + " + gunan(karana=" + orig(2) + ", sahakarana=" + orig(3) + ")";
    }

    // Bhagaphalam (Division)
    std::regex bhagaphalam_pat1(R"((\w+)\s+ko\s+(\w+)\s+aur\s+(\w+)\s+ka\s+bhagaphalam\s+rkho)");
    std::regex bhagaphalam_pat2(R"(set\s+(\w+)\s+as\s+division\s+of\s+(\w+)\s+and\s+(\w+))");
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

    std::regex inc_pat1(R"((\w+)\s+ko\s+(\w+)\s+se\s+badhao)");
    std::regex inc_pat2(R"(add\s+(\w+)\s+to\s+(\w+))");
    std::regex inc_pat3(R"((\w+)\s+me\s+(\w+)\s+(?:jod|add))");
    if (std::regex_search(lower_l, match, inc_pat1)) {
        return orig(1) + " + vrdh(karana=" + orig(2) + ")";
    }
    if (std::regex_search(lower_l, match, inc_pat2)) {
        return orig(2) + " + vrdh(karana=" + orig(1) + ")";
    }
    if (std::regex_search(lower_l, match, inc_pat3)) {
        return orig(1) + " + vrdh(karana=" + orig(2) + ")";
    }

    std::regex dec_pat1(R"((\w+)\s+ko\s+(\w+)\s+se\s+kam\s+karo)");
    std::regex dec_pat2(R"(subtract\s+(\w+)\s+from\s+(\w+))");
    std::regex dec_pat3(R"((\w+)\s+se\s+(\w+)\s+(?:kam|minus|ghata))");
    if (std::regex_search(lower_l, match, dec_pat1)) {
        return orig(1) + " + hras(karana=" + orig(2) + ")";
    }
    if (std::regex_search(lower_l, match, dec_pat2)) {
        return orig(2) + " + hras(karana=" + orig(1) + ")";
    }
    if (std::regex_search(lower_l, match, dec_pat3)) {
        return orig(1) + " + hras(karana=" + orig(2) + ")";
    }

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

    std::regex loop_pat1(R"(loop\s+chalao\s+jab\s+tak\s+(\w+)\s+(\w+)\s+se\s+chota)");
    std::regex loop_pat2(R"(while\s+(\w+)\s+is\s+less\s+than\s+(\w+))");
    if (std::regex_search(lower_l, match, loop_pat1) ||
        std::regex_search(lower_l, match, loop_pat2)) {
        return orig(1) + " + pravah(seema=" + orig(2) + ")";
    }

    std::regex mult_pat1(R"((\w+)\s+ko\s+(\w+)\s+se\s+guna\s+karo)");
    std::regex mult_pat2(R"(multiply\s+(\w+)\s+by\s+(\w+))");
    if (std::regex_search(lower_l, match, mult_pat1) ||
        std::regex_search(lower_l, match, mult_pat2)) {
        return orig(1) + " + gun(karana=" + orig(2) + ")";
    }

    std::regex div_pat1(R"((\w+)\s+ko\s+(\w+)\s+se\s+bhag\s+do)");
    std::regex div_pat2(R"(divide\s+(\w+)\s+by\s+(\w+))");
    if (std::regex_search(lower_l, match, div_pat1) ||
        std::regex_search(lower_l, match, div_pat2)) {
        return orig(1) + " + bhag(karana=" + orig(2) + ")";
    }

    std::regex cond_pat1(R"(agar\s+(\w+)\s+(\w+)\s+se\s+bada\s+ho)");
    std::regex cond_pat2(R"(agar\s+(\w+)\s+(\w+)\s+se\s+chota\s+ho)");
    std::regex cond_pat3(R"(agar\s+(\w+)\s+(\w+)\s+(?:ke\s+barabar|barabar)\s+ho)");
    std::regex cond_pat4(R"(if\s+(\w+)\s+is\s+greater\s+than\s+(\w+))");
    std::regex cond_pat5(R"(if\s+(\w+)\s+is\s+less\s+than\s+(\w+))");
    std::regex cond_pat6(R"(if\s+(\w+)\s+is\s+equal\s+to\s+(\w+))");
    
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
            return {"", "", {}, {}};
        }

        // Auto-translate if it's natural language vibe prompt
        if (line.find('+') == std::string::npos && line != "pravah_khatam" && line != "sankalpa_khatam") {
            std::string translated = translate_natural_prompt(line);
            if (translated != line) {
                std::cout << COLOR_BLUE << "[Vibe -> Sanskrit] " << COLOR_RESET << line << " ➔ " << COLOR_YELLOW << translated << COLOR_RESET << std::endl;
                line = translated;
            } else {
                throw std::runtime_error("Unknown syntax. No Paninian '+' operator, and could not parse as a conversational vibe prompt: '" + line + "'");
            }
        }

        // Check for block terminators
        if (line == "pravah_khatam") {
            return {"pravah_khatam", "", {}, {}};
        }
        if (line == "sankalpa_khatam") {
            return {"sankalpa_khatam", "", {}, {}};
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

        return {kriya, karta, args, {}};
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
                if (inst.kriya.empty()) continue; // Skip comments/empty lines

                if (inst.kriya == "pravah_khatam" || inst.kriya == "sankalpa_khatam") {
                    if (loop_stack.empty()) {
                        throw std::runtime_error("Orphan '" + inst.kriya + "' (block end) without matching block start.");
                    }
                    if (inst.kriya == "pravah_khatam" && loop_stack.back()->kriya != "pravah") {
                        throw std::runtime_error("Mismatched loop block end: expected 'pravah_khatam'.");
                    }
                    if (inst.kriya == "sankalpa_khatam" && loop_stack.back()->kriya != "sankalpa") {
                        throw std::runtime_error("Mismatched conditional block end: expected 'sankalpa_khatam'.");
                    }
                    loop_stack.pop_back();
                } else if (inst.kriya == "pravah" || inst.kriya == "sankalpa") {
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
            std::cerr << COLOR_RED << "Compilation Error: Unterminated loop block at end of file." << COLOR_RESET << std::endl;
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

// SutraVM: C++ execution runtime from scratch
class SutraVM {
private:
    std::unordered_map<std::string, Variable> karta_registry;

    void log(const std::string& msg) {
        std::cout << COLOR_YELLOW << "[SutraVM] " << COLOR_RESET << msg << std::endl;
    }

    int resolve_value(const std::string& arg) {
        if (karta_registry.find(arg) != karta_registry.end()) {
            if (karta_registry[arg].is_string) {
                try {
                    return std::stoi(karta_registry[arg].str_val);
                } catch (...) {
                    return 0;
                }
            }
            return karta_registry[arg].int_val;
        }
        try {
            return std::stoi(arg);
        } catch (...) {
            return 0;
        }
    }

    std::string resolve_string(const std::string& arg) {
        if (karta_registry.find(arg) != karta_registry.end()) {
            if (karta_registry[arg].is_string) {
                return karta_registry[arg].str_val;
            }
            return std::to_string(karta_registry[arg].int_val);
        }
        std::string s = arg;
        if (s.size() >= 2 && s.front() == '"' && s.back() == '"') {
            s = s.substr(1, s.size() - 2);
        }
        return s;
    }

public:
    void execute(const std::vector<Instruction>& program) {
        for (const auto& inst : program) {
            if (inst.kriya == "sruj") { // Srujana - Create variable
                Variable var;
                if (inst.args.find("maan") != inst.args.end()) {
                    std::string val_str = inst.args.at("maan");
                    if (val_str.size() >= 2 && val_str.front() == '"' && val_str.back() == '"') {
                        var.is_string = true;
                        var.str_val = val_str.substr(1, val_str.size() - 2);
                    } else if (karta_registry.find(val_str) != karta_registry.end()) {
                        var = karta_registry[val_str];
                    } else {
                        try {
                            var.int_val = std::stoi(val_str);
                        } catch (...) {
                            var.is_string = true;
                            var.str_val = val_str;
                        }
                    }
                }
                karta_registry[inst.karta] = var;
                if (var.is_string) {
                    log("Srujana: Created variable '" + inst.karta + "' with Maan = \"" + var.str_val + "\"");
                } else {
                    log("Srujana: Created variable '" + inst.karta + "' with Maan = " + std::to_string(var.int_val));
                }
            }
            else if (inst.kriya == "vrdh") { // Vardhanam - Increment/Add
                if (karta_registry.find(inst.karta) == karta_registry.end()) {
                    throw std::runtime_error("Variable '" + inst.karta + "' not declared before Vardhanam.");
                }
                int add_val = 1;
                if (inst.args.find("karana") != inst.args.end()) {
                    add_val = resolve_value(inst.args.at("karana"));
                }
                karta_registry[inst.karta].int_val += add_val;
                log("Vardhanam: '" + inst.karta + "' increased by " + std::to_string(add_val) + ". New Maan = " + std::to_string(karta_registry[inst.karta].int_val));
            }
            else if (inst.kriya == "hras") { // Hrasanam - Decrement/Subtract
                if (karta_registry.find(inst.karta) == karta_registry.end()) {
                    throw std::runtime_error("Variable '" + inst.karta + "' not declared before Hrasanam.");
                }
                int sub_val = 1;
                if (inst.args.find("karana") != inst.args.end()) {
                    sub_val = resolve_value(inst.args.at("karana"));
                }
                karta_registry[inst.karta].int_val -= sub_val;
                log("Hrasanam: '" + inst.karta + "' decreased by " + std::to_string(sub_val) + ". New Maan = " + std::to_string(karta_registry[inst.karta].int_val));
            }
            else if (inst.kriya == "drsh") { // Darshanam - Display
                if (karta_registry.find(inst.karta) != karta_registry.end()) {
                    if (karta_registry[inst.karta].is_string) {
                        std::cout << COLOR_GREEN << "➔ [DARSHANAM] " << inst.karta << " = \"" << karta_registry[inst.karta].str_val << "\"" << COLOR_RESET << std::endl;
                    } else {
                        std::cout << COLOR_GREEN << "➔ [DARSHANAM] " << inst.karta << " = " << karta_registry[inst.karta].int_val << COLOR_RESET << std::endl;
                    }
                } else {
                    std::string out = inst.karta;
                    if (out.size() >= 2 && out.front() == '"' && out.back() == '"') {
                        out = out.substr(1, out.size() - 2);
                    }
                    std::cout << COLOR_GREEN << "➔ [DARSHANAM] " << out << COLOR_RESET << std::endl;
                }
            }
            else if (inst.kriya == "gun") { // Guna - Multiply
                if (karta_registry.find(inst.karta) == karta_registry.end()) {
                    throw std::runtime_error("Variable '" + inst.karta + "' not declared before Guna.");
                }
                int mult_val = 1;
                if (inst.args.find("karana") != inst.args.end()) {
                    mult_val = resolve_value(inst.args.at("karana"));
                }
                karta_registry[inst.karta].int_val *= mult_val;
                log("Guna: '" + inst.karta + "' multiplied by " + std::to_string(mult_val) + ". New Maan = " + std::to_string(karta_registry[inst.karta].int_val));
            }
            else if (inst.kriya == "bhag") { // Bhaga - Divide
                if (karta_registry.find(inst.karta) == karta_registry.end()) {
                    throw std::runtime_error("Variable '" + inst.karta + "' not declared before Bhaga.");
                }
                int div_val = 1;
                if (inst.args.find("karana") != inst.args.end()) {
                    div_val = resolve_value(inst.args.at("karana"));
                }
                if (div_val == 0) {
                    throw std::runtime_error("Mathematical error: Division by zero is not allowed.");
                }
                karta_registry[inst.karta].int_val /= div_val;
                log("Bhaga: '" + inst.karta + "' divided by " + std::to_string(div_val) + ". New Maan = " + std::to_string(karta_registry[inst.karta].int_val));
            }
            else if (inst.kriya == "yog") { // Yog - Complex Addition / Set value to sum of two operands
                Variable var;
                int val1 = resolve_value(inst.args.at("karana"));
                int val2 = resolve_value(inst.args.at("sahakarana"));
                var.int_val = val1 + val2;
                karta_registry[inst.karta] = var;
                log("Yog: Set '" + inst.karta + "' to " + std::to_string(val1) + " + " + std::to_string(val2) + " = " + std::to_string(var.int_val));
            }
            else if (inst.kriya == "antar") { // Antar - Subtraction / Set value to difference of two operands
                Variable var;
                int val1 = resolve_value(inst.args.at("karana"));
                int val2 = resolve_value(inst.args.at("sahakarana"));
                var.int_val = val1 - val2;
                karta_registry[inst.karta] = var;
                log("Antar: Set '" + inst.karta + "' to " + std::to_string(val1) + " - " + std::to_string(val2) + " = " + std::to_string(var.int_val));
            }
            else if (inst.kriya == "gunan") { // Gunan - Multiplication / Set value to product of two operands
                Variable var;
                int val1 = resolve_value(inst.args.at("karana"));
                int val2 = resolve_value(inst.args.at("sahakarana"));
                var.int_val = val1 * val2;
                karta_registry[inst.karta] = var;
                log("Gunan: Set '" + inst.karta + "' to " + std::to_string(val1) + " * " + std::to_string(val2) + " = " + std::to_string(var.int_val));
            }
            else if (inst.kriya == "bhagaphalam") { // Bhagaphalam - Division / Set value to division of two operands
                Variable var;
                int val1 = resolve_value(inst.args.at("karana"));
                int val2 = resolve_value(inst.args.at("sahakarana"));
                if (val2 == 0) {
                    throw std::runtime_error("Mathematical error: Division by zero in Bhagaphalam.");
                }
                var.int_val = val1 / val2;
                karta_registry[inst.karta] = var;
                log("Bhagaphalam: Set '" + inst.karta + "' to " + std::to_string(val1) + " / " + std::to_string(val2) + " = " + std::to_string(var.int_val));
            }
            else if (inst.kriya == "sandh") { // Sandh - String Concatenation / Set value to concatenation of two strings
                Variable var;
                var.is_string = true;
                std::string s1 = resolve_string(inst.args.at("karana"));
                std::string s2 = resolve_string(inst.args.at("sahakarana"));
                var.str_val = s1 + s2;
                karta_registry[inst.karta] = var;
                log("Sandh: Concatenated \"" + s1 + "\" and \"" + s2 + "\" to set '" + inst.karta + "' = \"" + var.str_val + "\"");
            }
            else if (inst.kriya == "sankalpa") { // Sankalpa - Conditional Branching
                if (karta_registry.find(inst.karta) == karta_registry.end()) {
                    throw std::runtime_error("Condition variable '" + inst.karta + "' not declared before Sankalpa.");
                }
                if (inst.args.find("sharta") == inst.args.end() || inst.args.find("karana") == inst.args.end()) {
                    throw std::runtime_error("Sankalpa Kriya requires 'sharta' and 'karana' comparison values.");
                }
                std::string sharta = inst.args.at("sharta");
                int val = resolve_value(inst.karta);
                int comp = resolve_value(inst.args.at("karana"));
                bool condition_met = false;
                
                if (sharta == "bada") condition_met = (val > comp);
                else if (sharta == "chota") condition_met = (val < comp);
                else if (sharta == "barabar") condition_met = (val == comp);
                
                if (condition_met) {
                    execute(inst.sub_instructions);
                }
            }
            else if (inst.kriya == "pravah") { // Pravahanam - Loop
                if (karta_registry.find(inst.karta) == karta_registry.end()) {
                    throw std::runtime_error("Loop variable '" + inst.karta + "' not declared before Pravahanam.");
                }
                if (inst.args.find("seema") == inst.args.end()) {
                    throw std::runtime_error("Loop Kriya requires a limit parameter 'seema=value'.");
                }
                int limit = resolve_value(inst.args.at("seema"));
                log("Pravahanam: Starting loop on '" + inst.karta + "' up to seema " + std::to_string(limit));

                while (karta_registry[inst.karta].int_val < limit) {
                    execute(inst.sub_instructions);
                }
                log("Pravahanam: Loop ended.");
            }
        }
    }
};

void run_repl() {
    SutraCompiler compiler;
    SutraVM vm;
    std::string line;
    std::cout << COLOR_BLUE << "Interactive REPL Mode initialized. Type your Paninian code line-by-line." << COLOR_RESET << std::endl;
    std::cout << "Type 'exit' to terminate shell session." << std::endl;
    int line_num = 1;

    while (true) {
        std::cout << COLOR_CYAN << "sutra> " << COLOR_RESET;
        if (!std::getline(std::cin, line)) break;
        std::string trimmed = trim(line);
        if (trimmed == "exit") {
            std::cout << "Shutting down SutraVM..." << std::endl;
            break;
        }
        if (trimmed.empty()) continue;

        try {
            Instruction inst = compiler.compile_line(line, line_num++);
            if (!inst.kriya.empty()) {
                if (inst.kriya == "pravah") {
                    std::cout << COLOR_RED << "REPL Error: Loops ('pravah') cannot be run interactively in single-line mode. Save to a file to run loop structures." << COLOR_RESET << std::endl;
                    continue;
                }
                std::vector<Instruction> prog = {inst};
                vm.execute(prog);
            }
        } catch (const std::exception& e) {
            std::cerr << COLOR_RED << "Syntax/Runtime Error: " << e.what() << COLOR_RESET << std::endl;
        }
    }
}

int main(int argc, char* argv[]) {
    std::cout << COLOR_CYAN << "==========================================" << COLOR_RESET << std::endl;
    std::cout << COLOR_CYAN << "  SUTRA: Pure Paninian C++ Compiler/VM   " << COLOR_RESET << std::endl;
    std::cout << COLOR_CYAN << "==========================================" << COLOR_RESET << std::endl;

    if (argc < 2) {
        run_repl();
        return 0;
    }

    try {
        SutraCompiler compiler;
        std::vector<Instruction> program = compiler.compile_program(argv[1]);

        SutraVM vm;
        vm.execute(program);
    } catch (const std::exception& e) {
        std::cerr << COLOR_RED << "Runtime Error: " << e.what() << COLOR_RESET << std::endl;
        return 1;
    }

    return 0;
}
