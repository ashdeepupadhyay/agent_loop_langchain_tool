# agent_loop_langchain_tool

# how to run 
source .venv_1/bin/activate
uv run --active python main.py

        query 
          |
          |
        Thought-------------- Answer
        /     \
    Action   Observation
        \      /
          Tool

# without lang chain tool 

uv run --active python 2_agent_loop_raw_function_calling.py

https://docs.ollama.com/capabilities/tool-calling#calling-a-single-tool