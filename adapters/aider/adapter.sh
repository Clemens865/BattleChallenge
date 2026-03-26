#!/bin/bash
# BattleChallenge reference adapter for Aider
# Input: $TASK_FILE contains the task requirements
# Input: $OUTPUT_DIR is where to put generated files
# Output: Generated files in $OUTPUT_DIR

cd "$OUTPUT_DIR"
aider --message-file "$TASK_FILE" --yes --auto-commits
