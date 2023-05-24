# common VARS and EXPORTS
## EXPORTS
export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash
export TOPLEVEL_LANG ?= verilog

## PATHS
GIT_ROOT=$(shell git rev-parse --show-toplevel)
SUBMOD_PATH=$(GIT_ROOT)/submodules
VERINOC_PATH=$(SUBMOD_PATH)/verinoc
CDC_PATH=$(SUBMOD_PATH)/cdc
ASYNC_SRCS_DIR=$(CDC_PATH)/src
SYNC_SRC_DIR=$(VERINOC_PATH)/srcs

## VARS
export COCOTB_HDL_TIMEUNIT      = 1ns
export COCOTB_HDL_TIMEPRECISION = 1ns
SIM ?= icarus

# VERILOG SOURCES
VERILOG_SOURCES = $(SYNC_SRC_DIR)/components/circ_fifo.v 		# SYNC
VERILOG_SOURCES += $(shell find $(ASYNC_SRCS_DIR) | grep .sv) # ASYNC
VERILOG_SOURCES += tb_top.v

TOPLEVEL := tb_top
MODULE   := test

# PARAMS

include $(shell cocotb-config --makefiles)/Makefile.sim