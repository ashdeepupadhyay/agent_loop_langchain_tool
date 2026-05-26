# from dotenv import load_dotenv

# load_dotenv()

# import re
# import inspect   
# import ollama
# MAX_ITERATIONS = 10
# MODEL = "qwen3:1.7b"

# # --- Tools (LangChain @tool decorator) ---


# def get_product_price(product: str) -> float:
#     """Look up the price of a product in a catalog"""
#     print(f">> Executing get_product_price (product= '{product}')")
#     prices = {"laptop": 1299.99, "keyboard": 89.50, "headphones": 149.95}
#     return prices.get(product, 0.0)


# def apply_discount(price: float, discount_tier: str) -> float:
#     """Apply a discount tier to a price and return the final price
#     Available tiers: bronze, silver, gold
#     """
#     price = float(price)
#     print(f">> Executing apply_discount (price= '{price}', discount_tier= {discount_tier})")
#     discount_percentages = {"bronze": 5, "silver": 12, "gold": 23}
#     discount = discount_percentages.get(discount_tier, 0)
#     return round(price * (1 - discount / 100), 2)


# tools = {
#     "get_product_price": get_product_price,
#     "apply_discount": apply_discount
# }

# def get_tools_descriptions(tools_dict):
#     descriptions = []
#     for tool_name, tool_function in tools_dict.items():
#         original_function = getattr(tool_function, "__wrapped__", tool_function)
#         signature = inspect.signature(original_function)
#         docstring = inspect.getdoc(tool_function) or ""
#         descriptions.append(f"{tool_name}{signature}-{docstring}")
#     return "\n".join(descriptions)

# tools_descriptions = get_tools_descriptions(tools)
# tool_names = ", ".join(tools.keys())

# # react_prompt = """You are a helpful assistant.
# #                    You have access to a product catalog
# #                    and a discount tool\n\n
# #                    STRICT RULES - you must follow these exactly
# #                    1.Never guess or assume any product price
# #                    You must call get_product_price to get the real price.\n
# #                    2.Only call apply_discount after you have received
# #                     a price from get_product_price. Pass the exact price
# #                     returned by get_product_price - do not pass a made-up number\n
# #                     3. Never calculate discount percentages yourself. Always use the apply_discount tool.\n
# #                     4. If the user does not specify a discount, you must ask them which tier to use - do NOT assume one.
                    
# #                     Answer the following questions as best you can. You have access to the following tools:

# # {tools_descriptions}

# # Use the following format:

# # Question: the input question you must answer
# # Thought: you should always think about what to do
# # Action: the action to take, should be one of [{tool_names}]
# # Action Input: the input to the action
# # Observation: the result of the action
# # ... (this Thought/Action/Action Input/Observation can repeat N times)
# # Thought: I now know the final answer
# # Final Answer: the final answer to the original input question

# # Begin!

# # Question: {{question}}
# # Thought:""
# # """

# react_prompt = """You are a helpful assistant.
# ... (keep your existing rules) ...

# Use the following format:
# Question: the input question you must answer
# Thought: you should always think about what to do
# Action: the action to take, should be one of [{tool_names}]
# Action Input: the input to the action
# Observation: the result of the action
# ... (repeat)
# Final Answer: the final answer

# ---
# EXAMPLE:
# Question: What is the price of a keyboard?
# Thought: I need to look up the price for the keyboard.
# Action: get_product_price
# Action Input: {"product": "keyboard"}
# ---

# Begin!

# Question: {{question}}
# Thought:"""


# # @traceable(name="Ollama Chat", run_type="llm")
# def ollama_chat_traced(model,messages,options):
#     return ollama.chat(model=model, messages=messages,options=options)

# # --- agent loop ---

# # @traceable(name="LangChain Agent Loop")
# def run_agent(question:str):
    

#     print(f"Question: {question}")
#     print("="*60)

#     # prompt = react_prompt.format(tools_descriptions=tools_descriptions,tool_names=tool_names,question=question)
#     prompt = react_prompt.format(
#     tools_descriptions=tools_descriptions, 
#     tool_names=tool_names, 
#     question=question
# )
#     scratchpad = ""

    
#     for iteration in range(1,MAX_ITERATIONS+1):
#         print(f"--- Iteration {iteration} ---")
#         # ai_message = llm_with_tools.invoke(messages)
#         # Difference 4: ollama.chat() directly instead of llm_with_tools.invoke()
#         full_prompt = prompt + scratchpad

#         response = ollama_chat_traced(
#             model=MODEL,
#             messages=[{"role":"user","content":full_prompt}],
#             options={"stop":["\nObservation"],"temperature":0}

#         )
#         output = response.message.content

#         print(f"LLM Output:\n {output}")
#         print(f"[Parsing] Looking for Final Answer in LLM output ...")
#         final_answer_match = re.search(r"Final Answer:\s*(.+)", output, re.IGNORECASE)
#         if final_answer_match:
#             final_answer = final_answer_match.group(1).strip()
#             print(f"[parsed] Final Answer: {final_answer}")
#             print("="*60)
#             print(f"Final Answer: {final_answer}")
#             return final_answer

#         print(f"[Parsing] Looking for Action and Action Input in LLM output ...")
#         action_match = re.search(r"Action:\s*(.+)", output, re.IGNORECASE)
#         action_input_match = re.search(r"Action Input:\s*(.+)", output, re.IGNORECASE)

#         if action_match and action_input_match:
#             tool_name = action_match.group(1).strip()
#             tool_input_raw = action_input_match.group(1).strip()
#             print(f"[parsed] Tool Name: {tool_name}")
#             print(f"[parsed] Tool Input: {tool_input_raw}")
#         else:
#             print("[Parsing] Error Could not parse Action/Action Input from LLM Output.")
#             break
    
#         print(f"[Tool Selected]: {tool_name} with args {tool_input_raw}")

#         raw_args = [x.strip() for x in tool_input_raw.split(",")]
#         args = [x.split("=",1)[-1].strip().strip("'\"") for x in raw_args]

#         print(f"[Tool Executing] {tool_name} {{args}}...")
#         if tool_name not in tools:
#             observation = f"Error: tool '{tool_name}' not found.Available tools are: {list(tools.keys())}"
#         else:
#             observation = str(tools[tool_name](*args))

#         print(f"Tool Result: {observation}")

#         scratchpad+=f"{output}\nObservation: {observation}\nThought"

#     print(f"Reached max iterations ({MAX_ITERATIONS}) without a final answer.")
#     return None


# def main():
#     print("Hello from agent-loop-langchain-tool!")
#     print("Hello langChain Agent (.bind_tools)!")
#     print()
#     run_agent("What is the price of a laptop with a silver discount?")


# if __name__ == "__main__":
#     main()





# from dotenv import load_dotenv

# load_dotenv()

# import re
# import inspect   
# import ollama
# import json

# MAX_ITERATIONS = 10
# MODEL = "qwen3:1.7b"

# # --- Tools ---

# def get_product_price(product: str) -> float:
#     """Look up the price of a product in a catalog"""
#     print(f">> Executing get_product_price (product= '{product}')")
#     prices = {"laptop": 1299.99, "keyboard": 89.50, "headphones": 149.95}
#     return prices.get(product, 0.0)

# def apply_discount(price: float, discount_tier: str) -> float:
#     """Apply a discount tier to a price and return the final price
#     Available tiers: bronze, silver, gold
#     """
#     price = float(price)
#     print(f">> Executing apply_discount (price= '{price}', discount_tier= {discount_tier})")
#     discount_percentages = {"bronze": 5, "silver": 12, "gold": 23}
#     discount = discount_percentages.get(discount_tier, 0)
#     return round(price * (1 - discount / 100), 2)

# tools = {
#     "get_product_price": get_product_price,
#     "apply_discount": apply_discount
# }

# def get_tools_descriptions(tools_dict):
#     descriptions = []
#     for tool_name, tool_function in tools_dict.items():
#         original_function = getattr(tool_function, "__wrapped__", tool_function)
#         signature = inspect.signature(original_function)
#         docstring = inspect.getdoc(tool_function) or ""
#         descriptions.append(f"{tool_name}{signature}-{docstring}")
#     return "\n".join(descriptions)

# tools_descriptions = get_tools_descriptions(tools)
# tool_names = ", ".join(tools.keys())

# react_prompt = """You are a helpful assistant.
#                    You have access to a product catalog
#                    and a discount tool\n\n
#                    STRICT RULES - you must follow these exactly
#                    1.Never guess or assume any product price
#                    You must call get_product_price to get the real price.\n
#                    2.Only call apply_discount after you have received
#                     a price from get_product_price. Pass the exact price
#                     returned by get_product_price - do not pass a made-up number\n
#                     3. Never calculate discount percentages yourself. Always use the apply_discount tool.\n
#                     4. If the user does not specify a discount, you must ask them which tier to use - do NOT assume one.
                    
#                     Answer the following questions as best you can. You have access to the following tools:

# {tools_descriptions}

# Use the following format:

# Question: the input question you must answer
# Thought: you should always think about what to do
# Action: the action to take, should be one of [{tool_names}]
# Action Input: the input to the action
# Observation: the result of the action
# ... (this Thought/Action/Action Input/Observation can repeat N times)
# Thought: I now know the final answer
# Final Answer: the final answer to the original input question

# Begin!

# Question: {{question}}
# Thought:"""

# def ollama_chat_traced(model, messages, options):
#     return ollama.chat(model=model, messages=messages, options=options)

# def run_agent(question: str):
#     print(f"Question: {question}")
#     print("="*60)

#     prompt = react_prompt.format(tools_descriptions=tools_descriptions, tool_names=tool_names, question=question)
#     scratchpad = ""

#     for iteration in range(1, MAX_ITERATIONS + 1):
#         print(f"--- Iteration {iteration} ---")
#         full_prompt = prompt + scratchpad

#         response = ollama_chat_traced(
#             model=MODEL,
#             messages=[{"role": "user", "content": full_prompt}],
#             options={"stop": ["\nObservation"], "temperature": 0}
#         )
        
#         # FIX 1: Access .content directly to avoid TypeError
#         output = response.message.content

#         print(f"LLM Output:\n {output}")
#         print(f"[Parsing] Looking for Final Answer in LLM output ...")
#         final_answer_match = re.search(r"Final Answer:\s*(.+)", output, re.IGNORECASE)
#         if final_answer_match:
#             final_answer = final_answer_match.group(1).strip()
#             print(f"[parsed] Final Answer: {final_answer}")
#             print("="*60)
#             print(f"Final Answer: {final_answer}")
#             return final_answer

#         print(f"[Parsing] Looking for Action and Action Input in LLM output ...")
#         action_match = re.search(r"Action:\s*(.+)", output, re.IGNORECASE)
#         action_input_match = re.search(r"Action Input:\s*(.+)", output, re.IGNORECASE)

#         if action_match and action_input_match:
#             tool_name = action_match.group(1).strip()
#             tool_input_raw = action_input_match.group(1).strip()
#             print(f"[parsed] Tool Name: {tool_name}")
#             print(f"[parsed] Tool Input: {tool_input_raw}")
#         else:
#             print("[Parsing] Error Could not parse Action/Action Input from LLM Output.")
#             break
    
#         # FIX 2: Handle JSON tool inputs (common with models like Qwen)
#         try:
#             parsed_input = json.loads(tool_input_raw)
#             if isinstance(parsed_input, dict):
#                 args = list(parsed_input.values())
#             else:
#                 args = [parsed_input]
#         except json.JSONDecodeError:
#             # Fallback to the original simple split logic if not JSON
#             raw_args = [x.strip() for x in tool_input_raw.split(",")]
#             args = [x.split("=", 1)[-1].strip().strip("'\"") for x in raw_args]

#         print(f"[Tool Executing] {tool_name} with args {args}...")
#         if tool_name not in tools:
#             observation = f"Error: tool '{tool_name}' not found. Available tools are: {list(tools.keys())}"
#         else:
#             try:
#                 observation = str(tools[tool_name](*args))
#             except Exception as e:
#                 observation = f"Error executing tool: {str(e)}"

#         print(f"Tool Result: {observation}")
#         scratchpad += f"{output}\nObservation: {observation}\nThought: "

#     print(f"Reached max iterations ({MAX_ITERATIONS}) without a final answer.")
#     return None

# def main():
#     print("Hello from agent-loop-langchain-tool!")
#     print("Hello langChain Agent (.bind_tools)!")
#     print()
#     run_agent("What is the price of a laptop with a silver discount?")

# if __name__ == "__main__":
#     main()




from dotenv import load_dotenv
import re
import inspect   
import ollama
import json  # Added for robust parsing

load_dotenv()

MAX_ITERATIONS = 10
MODEL = "qwen3:1.7b"

# --- Tools ---

def get_product_price(product: str) -> float:
    """Look up the price of a product in a catalog"""
    # Clean input: lowercase and strip quotes
    product = str(product).strip().strip("'\"").lower()
    print(f">> Executing get_product_price (product= '{product}')")
    prices = {"laptop": 1299.99, "keyboard": 89.50, "headphones": 149.95}
    return prices.get(product, 0.0)

def apply_discount(price: float, discount_tier: str) -> float:
    """Apply a discount tier to a price and return the final price"""
    try:
        price = float(price)
    except:
        price = 0.0
    discount_tier = str(discount_tier).strip().strip("'\"").lower()
    print(f">> Executing apply_discount (price= '{price}', discount_tier= {discount_tier})")
    discount_percentages = {"bronze": 5, "silver": 12, "gold": 23}
    discount = discount_percentages.get(discount_tier, 0)
    return round(price * (1 - discount / 100), 2)

tools = {
    "get_product_price": get_product_price,
    "apply_discount": apply_discount
}

def get_tools_descriptions(tools_dict):
    descriptions = []
    for tool_name, tool_function in tools_dict.items():
        original_function = getattr(tool_function, "__wrapped__", tool_function)
        signature = inspect.signature(original_function)
        docstring = inspect.getdoc(tool_function) or ""
        descriptions.append(f"{tool_name}{signature}-{docstring}")
    return "\n".join(descriptions)

tools_descriptions = get_tools_descriptions(tools)
tool_names = ", ".join(tools.keys())

# FIX: Doubled {{ }} around JSON example to prevent .format() KeyError
react_prompt = """You are a helpful assistant.
1. Never guess a price; call get_product_price.
2. Only call apply_discount after getting a price.
3. If no discount tier is mentioned, ask the user.

Available Tools:
{tools_descriptions}

Use the following format:
Question: the input question
Thought: your reasoning
Action: one of [{tool_names}]
Action Input: the input to the action
Observation: the result
... (repeat)
Final Answer: the final answer

---
EXAMPLE:
Question: What is the price of a keyboard?
Thought: I need to look up the price for the keyboard.
Action: get_product_price
Action Input: {{"product": "keyboard"}}
---

Begin!

Question: {question}
Thought:"""

def ollama_chat_traced(model, messages, options):
    return ollama.chat(model=model, messages=messages, options=options)

def run_agent(question: str):
    print(f"Question: {question}")
    print("="*60)

    # Clean the prompt formatting
    prompt = react_prompt.format(
        tools_descriptions=tools_descriptions, 
        tool_names=tool_names, 
        question=question
    )
    scratchpad = ""

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"--- Iteration {iteration} ---")
        full_prompt = prompt + scratchpad

        response = ollama_chat_traced(
            model=MODEL,
            messages=[{"role": "user", "content": full_prompt}],
            options={"stop": ["\nObservation"], "temperature": 0}
        )
        output = response.message.content

        print(f"LLM Output:\n {output}")
        
        final_answer_match = re.search(r"Final Answer:\s*(.+)", output, re.IGNORECASE)
        if final_answer_match:
            final_answer = final_answer_match.group(1).strip()
            print(f"Final Answer: {final_answer}")
            return final_answer

        action_match = re.search(r"Action:\s*(.+)", output, re.IGNORECASE)
        action_input_match = re.search(r"Action Input:\s*(.+)", output, re.IGNORECASE)

        if action_match and action_input_match:
            tool_name = action_match.group(1).strip()
            tool_input_raw = action_input_match.group(1).strip()
            
            # FIX: Robust JSON Parsing for Tool Inputs
            try:
                parsed_input = json.loads(tool_input_raw)
                if isinstance(parsed_input, dict):
                    args = list(parsed_input.values())
                else:
                    args = [parsed_input]
            except json.JSONDecodeError:
                # Fallback for plain text
                raw_args = [x.strip() for x in tool_input_raw.split(",")]
                args = [x.split("=", 1)[-1].strip().strip("'\"") for x in raw_args]

            print(f"[Tool Executing] {tool_name} with args {args}...")
            
            if tool_name not in tools:
                observation = f"Error: tool '{tool_name}' not found."
            else:
                try:
                    observation = str(tools[tool_name](*args))
                except Exception as e:
                    observation = f"Error: {str(e)}"
        else:
            print("Error: Could not parse Action/Input.")
            break

        print(f"Tool Result: {observation}")
        scratchpad += f"{output}\nObservation: {observation}\nThought: "

    return None

def main():
    run_agent("What is the price of a laptop with a silver discount?")

if __name__ == "__main__":
    main()
