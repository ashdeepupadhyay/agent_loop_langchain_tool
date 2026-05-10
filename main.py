from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import HumanMessage,SystemMessage,ToolMessage
MAX_ITERATIONS = 10
MODEL = "qwen3:1.7b"

# --- Tools (LangChain @tool decorator) ---

@tool
def get_product_price(product: str) -> float:
    """Look up the price of a product in a catalog"""
    print(f">> Executing get_product_price (product= '{product}')")
    prices = {"laptop": 1299.99, "keyboard": 89.50, "headphones": 149.95}
    return prices.get(product, 0.0)

@tool
def apply_discount(price: float, discount_tier: str) -> float:
    """Apply a discount tier to a price and return the final price
    Available tiers: bronze, silver, gold
    """
    print(f">> Executing apply_discount (price= '{price}', discount_tier= {discount_tier})")
    discount_percentages = {"bronze": 5, "silver": 12, "gold": 23}
    discount = discount_percentages.get(discount_tier, 0)
    return round(price * (1 - discount / 100), 2)

# --- agent loop ---

# @traceable(name="LangChain Agent Loop")
def run_agent(question:str):
    tools = [get_product_price,apply_discount]
    tools_dict = {tool.name: tool for tool in tools}
    

    llm = init_chat_model(f"ollama:{MODEL}",temperature=0)
    # llm = init_chat_model(f"openai:gpt-5",temperature=0)
    llm_with_tools = llm.bind_tools(tools)
    print(f"Question: {question}")
    print("="*60)

    messages = [
        SystemMessage(content=("You are a helpful assistant."
                      "You have access to a product catalog"
                      "and a discount tool\n\n"
                      "STRICT RULES - you must follow these exactly"
                      "1.Never guess or assume any product price"
                      "You must call get_product_price to get the real price.\n"
                      "2.Only call apply_discount after you have received"
                       "a price from get_product_price. Pass the exact price"
                       "returned by get_product_price - do not pass a made-up number\n")
    ),
    HumanMessage(content=question)
]
    for iteration in range(1,MAX_ITERATIONS+1):
        print(f"--- Iteration {iteration} ---")
        ai_message = llm_with_tools.invoke(messages)
        # response = llm_with_tools(messages)
        # print(f"Response: {response}")

        tool_calls = ai_message.tool_calls

        if not tool_calls:
            print("No tool calls, final response:")
            print(ai_message.content)
            return ai_message.content
        
        tool_call = tool_calls[0]
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args",{})
        tool_call_id = tool_call.get("id")

        print(f"Tool call: {tool_name} with args {tool_args}")

        tool_to_use = tools_dict.get(tool_name)

        observation = tool_to_use.invoke(tool_args)
        
        print(f"Observation: {observation}")

        messages.append(ai_message)
        messages.append(ToolMessage(content=str(observation), tool_call_id=tool_call_id))

    print(f"Reached max iterations ({MAX_ITERATIONS}) without a final answer.")
    return None


def main():
    print("Hello from agent-loop-langchain-tool!")
    print("Hello langChain Agent (.bind_tools)!")
    print()
    run_agent("What is the price of a laptop with a silver discount?")


if __name__ == "__main__":
    main()
