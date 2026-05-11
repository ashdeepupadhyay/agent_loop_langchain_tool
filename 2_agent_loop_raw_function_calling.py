from dotenv import load_dotenv

load_dotenv()

import ollama
MAX_ITERATIONS = 10
MODEL = "qwen3:1.7b"

# --- Tools (LangChain @tool decorator) ---


def get_product_price(product: str) -> float:
    """Look up the price of a product in a catalog"""
    print(f">> Executing get_product_price (product= '{product}')")
    prices = {"laptop": 1299.99, "keyboard": 89.50, "headphones": 149.95}
    return prices.get(product, 0.0)


def apply_discount(price: float, discount_tier: str) -> float:
    """Apply a discount tier to a price and return the final price
    Available tiers: bronze, silver, gold
    """
    print(f">> Executing apply_discount (price= '{price}', discount_tier= {discount_tier})")
    discount_percentages = {"bronze": 5, "silver": 12, "gold": 23}
    discount = discount_percentages.get(discount_tier, 0)
    return round(price * (1 - discount / 100), 2)

# Difference 2: without @tool we must manually define the JSON schema for each function.
# This is exactly what LangChain's @tool decorator generates automatically.
# from the function's type hints and docstrings.

tools_for_llm = [
    {
        "type":"function",
        "function":{
            "name":"get_product_price",
            "description":"Look up the price of a product in a catalog",
            "parameters":{
                "type":"object",
                "properties":{
                    "product": {
                        "type": "string",
                        "description": "The product name, e.g 'laptop', 'keyboard', or 'headphones'"
                    }
                },
                "required": ["product"]
            },
        },
    },
    {
        "type":"function",
        "function":{
            "name":"apply_discount",
            "description":"Apply a discount tier to a price and return the final price. Available tiers: bronze, silver, gold",
            "parameters":{
                "type":"object",
                "properties":{
                    "price": {
                        "type": "number",
                        "description": "The original price before discount"
                    },
                    "discount_tier": {
                        "type": "string",
                        "description": "The discount tier to apply - one of: bronze, silver, gold"
                    }
                },
                "required": ["price","discount_tier"]
            },
        },
    }
]

# NOTE: Ollama can also auto-generate these schemas if you pass the functions
# directly as tools (similar to LangChain's @tool decorator):
#   tools_for_llm = [get_product_price, apply_discount]
# However, this requires your docstrings to follow the Google docstring format
# so Ollama can parse parameter descriptions from the Args section. For example:
#   def get_product_price(product: str) -> float:
#       """Look up the price of a product in the catalog.
#
#       Args:
#           product: The product name, e.g. 'laptop', 'headphones', 'keyboard'.
#
#       Returns:
#           The price of the product, or 0 if not found.
#       """
# We keep the manual JSON version here so you can see what @tool hides from you.

# --- Helper: traced Ollama call ---
# Difference 3: Without LangChain, we must manually trace LLM calls for LangSmith.

# @traceable(name="Ollama Chat", run_type="llm")
def ollama_chat_traced(messages):
    return ollama.chat(model=MODEL, tools=tools_for_llm, messages=messages)

# --- agent loop ---

# @traceable(name="LangChain Agent Loop")
def run_agent(question:str):
    # tools = [get_product_price,apply_discount]
    # tools_dict = {tool.name: tool for tool in tools}
    tools_dict = {
        "get_product_price": get_product_price,
        "apply_discount": apply_discount,
    }


    # llm = init_chat_model(f"ollama:{MODEL}",temperature=0)
    # llm = init_chat_model(f"openai:gpt-5",temperature=0)
    # llm_with_tools = llm.bind_tools(tools)
    print(f"Question: {question}")
    print("="*60)

    messages = [
    #     SystemMessage(content=("You are a helpful assistant."
    #                   "You have access to a product catalog"
    #                   "and a discount tool\n\n"
    #                   "STRICT RULES - you must follow these exactly"
    #                   "1.Never guess or assume any product price"
    #                   "You must call get_product_price to get the real price.\n"
    #                   "2.Only call apply_discount after you have received"
    #                    "a price from get_product_price. Pass the exact price"
    #                    "returned by get_product_price - do not pass a made-up number\n")
    # ),
    # HumanMessage(content=question)
    {
        "role":"system",
        "content":("You are a helpful assistant."
                   "You have access to a product catalog"
                   "and a discount tool\n\n"
                   "STRICT RULES - you must follow these exactly"
                   "1.Never guess or assume any product price"
                   "You must call get_product_price to get the real price.\n"
                   "2.Only call apply_discount after you have received"
                    "a price from get_product_price. Pass the exact price"
                    "returned by get_product_price - do not pass a made-up number\n")
    },
    {
        "role": "user",
        "content": question
    }
]
    
    for iteration in range(1,MAX_ITERATIONS+1):
        print(f"--- Iteration {iteration} ---")
        # ai_message = llm_with_tools.invoke(messages)
        # Difference 4: ollama.chat() directly instead of llm_with_tools.invoke()
        response = ollama_chat_traced(messages=messages)
        ai_message = response.message

        tool_calls = ai_message.tool_calls

        # response = llm_with_tools(messages)
        # print(f"Response: {response}")

        # tool_calls = ai_message.tool_calls

        if not tool_calls:
            print("No tool calls, final response:")
            print(ai_message.content)
            return ai_message.content
        
        tool_call = tool_calls[0]

        # Difference 6: Attribute access (.function.name) instead of dict access (.get("name"))
        tool_name = tool_call.function.name
        tool_args = tool_call.function.arguments

        # tool_name = tool_call.get("name")
        # tool_args = tool_call.get("args",{})
        # tool_call_id = tool_call.get("id")

        print(f"Tool call: {tool_name} with args {tool_args}")

        tool_to_use = tools_dict.get(tool_name)
        if tool_to_use is None:
            raise ValueError(f"Tool '{tool_name}' not found")

        # Difference 7: Direct function call instead of tool.invoke()
        observation = tool_to_use(**tool_args)

        # observation = tool_to_use.invoke(tool_args)
        
        print(f"Observation: {observation}")

        messages.append(ai_message)
        messages.append(
            {
                "role": "tool",
                "content": str(observation),
            }
        )
        # messages.append(ToolMessage(content=str(observation), tool_call_id=tool_call_id))

    print(f"Reached max iterations ({MAX_ITERATIONS}) without a final answer.")
    return None


def main():
    print("Hello from agent-loop-langchain-tool!")
    print("Hello langChain Agent (.bind_tools)!")
    print()
    run_agent("What is the price of a laptop with a silver discount?")


if __name__ == "__main__":
    main()
