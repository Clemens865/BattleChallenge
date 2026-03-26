#!/bin/bash
# BattleChallenge adapter for lazy-fetch
# Wraps Claude Code with lazy-fetch's context and persistence layer
#
# Input: $TASK_FILE contains the task requirements
# Input: $OUTPUT_DIR is where to put generated files
# Output: Generated files in $OUTPUT_DIR

cd "$OUTPUT_DIR"

# Initialize lazy-fetch context so Claude Code has project awareness
lazy init 2>/dev/null || true

# Feed the task to Claude Code (which lazy-fetch wraps)
# --print outputs to stdout, but we need files written to $OUTPUT_DIR
claude -p "You are working in $(pwd). Read the following task requirements and create the solution files directly in the current directory. Write ONLY the code files, no explanations.

$(cat "$TASK_FILE")"
