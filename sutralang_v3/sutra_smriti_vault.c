/*
 * SutraLang v3 Core - AI Agent Smriti Vault Implementation
 */

#include <string.h>
#include "sutra_smriti_vault.h"

void sutra_smriti_init(SutraSmritiVault *vault) {
    vault->count = 0;
}

int sutra_smriti_put(SutraSmritiVault *vault, const char *key, const char *value) {
    for (int i = 0; i < vault->count; i++) {
        if (strcmp(vault->entries[i].key, key) == 0) {
            strncpy(vault->entries[i].value, value, 255);
            vault->entries[i].value[255] = '\0';
            return 0;
        }
    }
    if (vault->count >= MAX_SMRITI_ENTRIES) return -1;
    SutraSmritiEntry *e = &vault->entries[vault->count++];
    strncpy(e->key, key, 63); e->key[63] = '\0';
    strncpy(e->value, value, 255); e->value[255] = '\0';
    return 0;
}

const char *sutra_smriti_get(SutraSmritiVault *vault, const char *key) {
    for (int i = 0; i < vault->count; i++) {
        if (strcmp(vault->entries[i].key, key) == 0) {
            return vault->entries[i].value;
        }
    }
    return NULL;
}
