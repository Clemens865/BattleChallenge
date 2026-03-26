#!/bin/bash
# BattleChallenge reference adapter for LangGraph
# Input: $TASK_FILE contains the task requirements
# Input: $OUTPUT_DIR is where to put generated files
# Output: Generated files in $OUTPUT_DIR

python3 - <<'PYTHON'
import os
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic

task_file = os.environ["TASK_FILE"]
output_dir = os.environ["OUTPUT_DIR"]

with open(task_file) as f:
    task_content = f.read()

llm = ChatAnthropic(model="claude-opus-4-6")
response = llm.invoke(f"Complete this programming task. Output ONLY the code, no explanations:\n\n{task_content}")

# Write the generated code to output
output_path = os.path.join(output_dir, "solution.py")
with open(output_path, "w") as f:
    f.write(response.content)

PYTHON
