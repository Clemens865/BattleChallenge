#!/bin/bash
# BattleChallenge reference adapter for Claude Code
# Input: $TASK_FILE contains the task requirements
# Input: $OUTPUT_DIR is where to put generated files
# Output: Generated files in $OUTPUT_DIR

cat "$TASK_FILE" | claude --output-dir "$OUTPUT_DIR" --print
