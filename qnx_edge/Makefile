# ==============================================================================
# MedOrqis-QNX: Makefile for Dual-Target POSIX (Linux) & QNX Neutrino RTOS 8.0
# Standards: IEC 62304 Class C compliant / C99 standard
# ==============================================================================

CC ?= gcc
CFLAGS ?= -std=c99 -Wall -Wextra -Werror -pedantic -O2 -Iinclude -D_POSIX_C_SOURCE=200809L
LDFLAGS ?= -pthread

# Directories
BIN_DIR = bin
BUILD_DIR = build
SRC_DIR = src
TEST_DIR = tests

# QNX Cross-compiler settings
QNX_CC = qcc
QNX_ARCH ?= x86_64
QNX_TARGET = -Vgcc_nto$(QNX_ARCH)

# Targets
MONITOR_BIN = $(BIN_DIR)/medorqis_qnx_monitor
TEST_BIN = $(BIN_DIR)/test_news2_deterministic

# Sources
CORE_SRCS = $(SRC_DIR)/news2_deterministic.c \
            $(SRC_DIR)/patient_simulator.c \
            $(SRC_DIR)/vitals_acq.c

MONITOR_SRCS = $(CORE_SRCS) $(SRC_DIR)/qnx_monitor_main.c
TEST_SRCS = $(SRC_DIR)/news2_deterministic.c $(TEST_DIR)/test_news2_deterministic.c

.PHONY: all clean test monitor qnx help

all: monitor test

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Build Console Monitor (TUI)
monitor: $(BIN_DIR)
	$(CC) $(CFLAGS) $(MONITOR_SRCS) -o $(MONITOR_BIN) $(LDFLAGS)
	@echo "[SUCCESS] Built $(MONITOR_BIN) for POSIX/Linux"

# Build and Run Deterministic Unit Tests
test: $(BIN_DIR)
	$(CC) $(CFLAGS) $(TEST_SRCS) -o $(TEST_BIN) $(LDFLAGS)
	@echo "[RUNNING] Running C unit test suite..."
	@./$(TEST_BIN)

# QNX 8.0 Cross-Compilation Target
qnx:
	@which $(QNX_CC) >/dev/null 2>&1 || { \
		echo "[INFO] QNX SDP 8.0 toolchain ('$(QNX_CC)') not in current PATH."; \
		echo "[INFO] To cross-compile for QNX Neutrino RTOS 8.0 target:"; \
		echo "       1. Source your QNX SDP: source /path/to/qnx800/qnxsdp-env.sh"; \
		echo "       2. Run: make qnx QNX_ARCH=x86_64  (or aarch64)"; \
		exit 0; \
	}
	$(QNX_CC) $(QNX_TARGET) $(CFLAGS) $(MONITOR_SRCS) -o $(BIN_DIR)/medorqis_qnx_monitor.qnx $(LDFLAGS)
	@echo "[SUCCESS] Cross-compiled QNX 8.0 binary: $(BIN_DIR)/medorqis_qnx_monitor.qnx"

clean:
	rm -rf $(BIN_DIR) $(BUILD_DIR)
	@echo "[CLEAN] Removed build artifacts"

help:
	@echo "MedOrqis-QNX Build System"
	@echo "Usage:"
	@echo "  make monitor  - Build the bedside terminal telemetry monitor"
	@echo "  make test     - Build and run the deterministic C unit tests"
	@echo "  make qnx      - Cross-compile for QNX Neutrino RTOS 8.0"
	@echo "  make clean    - Remove build artifacts"
