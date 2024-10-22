SHELL := /bin/bash -o pipefail -o errexit

# Conda-related paths
CONDA_ENV_DIR := ./env
CONDA_ENV_FILE := environment.yml
CONDA_ENV_MARKER := $(CONDA_ENV_DIR)/.mark-environment-created

# Commands
CONDA_EXE ?= conda
conda_run := $(CONDA_EXE) run --live-stream --prefix $(CONDA_ENV_DIR)

# Command to create or update a conda environment.
# Uses a marker file to only perform the action if the $(CONDA_ENV_FILE) is changed.
$(CONDA_ENV_MARKER): $(CONDA_ENV_FILE)
	$(CONDA_EXE) env \
		$(shell [ -d $(CONDA_ENV_DIR) ] && echo update || echo create) \
		--prefix $(CONDA_ENV_DIR) \
		--file $(CONDA_ENV_FILE)
	touch $(CONDA_ENV_MARKER)

help:  ## Display help for the Makefile targets
	@@grep -h '^[a-zA-Z]' $(MAKEFILE_LIST) | awk -F ':.*?## ' 'NF==2 {printf "   %-20s%s\n", $$1, $$2}' | sort

setup: $(CONDA_ENV_MARKER)  ## Create or update local conda environment

test: setup  ## Run unit tests
	$(conda_run) pytest

.PHONY: $(MAKECMDGOALS)
