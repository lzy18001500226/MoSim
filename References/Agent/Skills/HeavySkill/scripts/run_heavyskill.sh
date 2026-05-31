#!/bin/bash
# HeavySkill — Example execution script
# Adjust the parameters below to match your setup.

set -e

# ============ Configuration ============
MODEL="deepseek-r1"                          # Model name for both reasoning and deliberation
API_BASE="http://localhost:8080"             # OpenAI-compatible API endpoint
API_KEY="EMPTY"                              # API key (set to your key if needed)

# Optional: use a different model for deliberation
# SUMMARY_MODEL="qwen3-32b"
# SUMMARY_API_BASE="http://localhost:8081"

# Pipeline parameters
REASON_K=8                                   # Number of parallel reasoning trajectories
SUMMARY_K=4                                  # Number of deliberation samples
ITERATIONS=1                                 # Number of iterative deliberation rounds

# Prompt configuration
PROMPT_TYPE="general"                        # "general" or "stem"
LANGUAGE="en"                                # "en" or "cn"

# ============ Single Query Mode ============
python scripts/run_heavyskill.py \
    --query "Let N be the greatest four-digit positive integer with the property that whenever one of its digits is changed to 1, the resulting number is divisible by 7. Let Q and R be the quotient and remainder, respectively, when N is divided by 1000. Find Q+R." \
    --model "$MODEL" \
    --api_base "$API_BASE" \
    --api_key "$API_KEY" \
    --reason_k $REASON_K \
    --summary_k $SUMMARY_K \
    --iterations $ITERATIONS \
    --prompt_type "$PROMPT_TYPE" \
    --language "$LANGUAGE" \
    --output "outputs/result.json" \
    --verbose

# ============ Batch Mode (from file) ============
# python scripts/run_heavyskill.py \
#     --input_file "examples/example_math.json" \
#     --model "$MODEL" \
#     --api_base "$API_BASE" \
#     --api_key "$API_KEY" \
#     --reason_k $REASON_K \
#     --summary_k $SUMMARY_K \
#     --output "outputs/batch_result.json" \
#     --verbose

# ============ With Separate Summary Model ============
# python scripts/run_heavyskill.py \
#     --query "Your query here" \
#     --model "$MODEL" \
#     --api_base "$API_BASE" \
#     --summary_model "$SUMMARY_MODEL" \
#     --summary_api_base "$SUMMARY_API_BASE" \
#     --reason_k $REASON_K \
#     --summary_k $SUMMARY_K \
#     --output "outputs/result_separate.json"
