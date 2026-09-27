/*
 * SutraLang v3 Core - Standalone Package Manager CLI (sutrapak)
 * ponytail: Minimal project generator & compilation orchestrator.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("SutraLang 3.0 Package Manager (sutrapak)\n");
        printf("Usage:\n");
        printf("  sutrapak new <project_name>   Create a new SutraLang project\n");
        printf("  sutrapak build                Compile project via sutrac\n");
        return 0;
    }

    if (strcmp(argv[1], "new") == 0 && argc >= 3) {
        const char *pname = argv[2];
        mkdir(pname, 0755);

        char main_path[256];
        snprintf(main_path, sizeof(main_path), "%s/main.sutra", pname);

        FILE *f = fopen(main_path, "w");
        if (f) {
            fprintf(f, "// %s - SutraLang 3.0 Native Project\n", pname);
            fprintf(f, "ek Karta title maan \"%s Initialized Successfully\"\n", pname);
            fprintf(f, "Karma title Karana Print\n");
            fclose(f);
            printf("[sutrapak] Created new SutraLang project '%s' at '%s'\n", pname, main_path);
        } else {
            fprintf(stderr, "Error creating project file\n");
            return 1;
        }
    } else if (strcmp(argv[1], "build") == 0) {
        int res = system("./sutrac main.sutra -o main_bin");
        if (res == 0) {
            printf("[sutrapak] Built target 'main_bin'\n");
        } else {
            fprintf(stderr, "[sutrapak] Build failed\n");
            return 1;
        }
    } else {
        printf("Unknown command: %s\n", argv[1]);
    }

    return 0;
}
