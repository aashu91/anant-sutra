/*
 * SutraOS Native 3.0 Engine Runtime Header
 * Paninian State Machine Primitive Actions for Sovereign Execution
 */

#ifndef SUTRA_OS_RUNTIME_H
#define SUTRA_OS_RUNTIME_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/sysinfo.h>
#include "sutra_mem.h"
#include "sutra_sys.h"
#include "sutra_io.h"
#include "sutra_smriti_vault.h"

// Telemetry state structure (Zero-GC stack/arena allocated)
typedef struct {
    long total_ram_mb;
    long free_ram_mb;
    float load_1m;
    float cpu_temp_c;
    int battery_pct;
    char battery_status[32];
} SutraOsTelemetry;

// Poly bhai Quantitative Signal Gating state
typedef struct {
    char market_slug[64];
    char side[16];
    double price;
    double edge;
    int signal_valid;
} SutraOsPolySignal;

// Expander Scheduler State (8 cores, 3-regular hypercube)
typedef struct {
    int cores[8][3];
    int core_load[8];
    int active_tasks;
} SutraOsScheduler;

// Function declarations
void sutra_os_runtime_init(void);
void sutra_os_action_SysTelemetry(void);
void sutra_os_action_PolyQuantGate(void);
void sutra_os_action_AnantAnaadiVault(void);
void sutra_os_action_SmritiSync(void);
void sutra_os_action_ExpanderScheduler(void);
void sutra_os_action_NyayaSandbox(void);
void sutra_os_action_KshamaSupervisor(void);
void sutra_os_action_DrishyaEngine(void);
void sutra_os_action_PravahLoop(void);
void sutra_os_action_SutraOSBoot(void);
void sutra_os_run_verification(void);

#endif // SUTRA_OS_RUNTIME_H
