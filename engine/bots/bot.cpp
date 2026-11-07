#include <iostream>
#include <string>
#include <cstdlib>

// Extract an integer value for the given JSON key.
static int get_int(const std::string& s, const std::string& key) {
    for (int space = 1; space >= 0; space--) {
        std::string k = "\"" + key + "\":" + (space ? " " : "");
        auto pos = s.find(k);
        if (pos == std::string::npos) continue;
        pos += k.size();
        while (pos < s.size() && s[pos] == ' ') pos++;
        return std::stoi(s.substr(pos));
    }
    return -1;
}

// Extract a string value for the given JSON key.
static std::string get_str(const std::string& s, const std::string& key) {
    for (int space = 1; space >= 0; space--) {
        std::string k = "\"" + key + "\":" + (space ? " \"" : "\"");
        auto pos = s.find(k);
        if (pos == std::string::npos) continue;
        pos += k.size();
        auto end = s.find('"', pos);
        return s.substr(pos, end - pos);
    }
    return "";
}

// Count ships in the "ships" array that belong to `player`.
static int count_own_ships(const std::string& line, int player) {
    std::string marker = "\"ships\": [";
    auto start = line.find(marker);
    if (start == std::string::npos) {
        marker = "\"ships\":[";
        start = line.find(marker);
        if (start == std::string::npos) return 0;
    }
    start += marker.size();

    std::string player_val = "\"player\": " + std::to_string(player);
    std::string player_val2 = "\"player\":" + std::to_string(player);

    int count = 0;
    size_t i = start;
    int depth = 1;
    while (i < line.size() && depth > 0) {
        if (line[i] == ']' && depth == 1) break;
        if (line[i] == '{') {
            size_t obj_start = i;
            int d = 1;
            i++;
            while (i < line.size() && d > 0) {
                if (line[i] == '{') d++;
                else if (line[i] == '}') d--;
                i++;
            }
            std::string obj = line.substr(obj_start, i - obj_start);
            if (obj.find(player_val) != std::string::npos ||
                obj.find(player_val2) != std::string::npos)
                count++;
            continue;
        }
        i++;
    }
    return count;
}

int main() {
    std::string line;
    std::getline(std::cin, line);

    int player = get_int(line, "player");
    int seed   = 1;
    srand(static_cast<unsigned>(seed));

    // Acknowledge init
    std::cout << "{\"type\": \"ack\", \"player\": " << player << "}" << std::endl;

    const std::string dirs[] = {"NORTH", "SOUTH", "EAST", "WEST", "STAY"};

    while (std::getline(std::cin, line)) {
        std::string type = get_str(line, "type");
        if (type == "done") break;
        if (type != "update") continue;

        int n = count_own_ships(line, player);
        if (n <= 0) n = 1;

        std::cout << "{\"type\": \"command\", \"player\": " << player
                  << ", \"commands\": [";
        for (int i = 0; i < n; i++) {
            if (i > 0) std::cout << ", ";
            std::cout << "\"" << dirs[rand() % 5] << "\"";
        }
        std::cout << "], \"build\": false}" << std::endl;
    }

    return 0;
}
