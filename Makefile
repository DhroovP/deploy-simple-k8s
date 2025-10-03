SHELL := /bin/bash

# .PHONY: all deps

# # Install dependencies if missing (idempotent)
# deps:
# 	brew install awscli || true
# 	brew install python@3.11 || true
# 	brew install jq || true
# 	brew install kubectl || true
# 	brew install eksctl || true
# 	brew install docker || true

# Load .env and run deploy script
all: 
	@echo "Loading environment variables from .env"
	@set -a; source .env; set +a; \
	python3 deploy.py
