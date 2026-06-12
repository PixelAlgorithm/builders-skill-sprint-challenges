"""
Challenge 4: The Full Agent — Tools + Memory + Streaming
Combine everything into one powerful agent.
Model: Amazon Nova Pro via Bedrock

Instructions:
  1. Fill in ALL the TODO sections
  2. Run: python starter.py
  3. Have a full conversation using all tools!
"""

import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"
import requests
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
MODEL = "us.amazon.nova-pro-v1:0"


# ============================================================
# TODO 1: Import everything you need
# ============================================================
# Hint: You need Agent, tool from strands
#       calculator, mem0_memory from strands_tools
from strands import Agent, tool
from strands_tools import calculator,mem0_memory
# Your imports here


# ============================================================
# TODO 2: Create a streaming callback handler
# ============================================================
# This function gets called for every chunk of text the agent generates
# Hint:
# def stream_callback(**kwargs):
#     if "data" in kwargs:
#         print(kwargs["data"], end="", flush=True)
#     elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
#         print(f"\n🔧 Using tool: {kwargs['current_tool_use']['name']}")

def stream_callback(**kwargs):
    if "data" in kwargs:
        print(kwargs["data"], end="", flush=True)
    elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
        print(f"\n🔧 Using tool: {kwargs['current_tool_use']['name']}")


# ============================================================
# TODO 3: Create custom tools — weather and age_calculator
# ============================================================
# Reuse your code from Challenge 2!

# Your tools here
@tool
def weather(city: str) -> str:
  """This tool is used to get weather for a city
    Args :
      city: name of the city
  """
  url= f"https://wttr.in/{city}?format=j1"
  response = requests.get(url)
  data = response.json()

  current = data["current_condition"][0]

  return (
        f"Weather in {city}: "
        f"{current['temp_C']}°C, "
        f"{current['weatherDesc'][0]['value']}"
    )


@tool
def age_calculator(birth_date: str) -> str:
    """Calculate age from a birth date."""

    birth_date = birth_date.replace("/", "-")

    dob = datetime.strptime(birth_date, "%Y-%m-%d").date()

    age = relativedelta(date.today(), dob)

    return f"{age.years} years, {age.months} months, {age.days} days"

# ============================================================
# TODO 4: Create the full agent with ALL tools + memory + streaming
# ============================================================
# Hint: Agent(
#     model=MODEL,
#     tools=[calculator, weather, age_calculator, mem0_memory],
#     callback_handler=stream_callback,
#     system_prompt="..."
# )

prompt = "You are a Ai assitent called Pixie ," \
"To resolve user query Use tools then give the answer"


agent = Agent(
    model=MODEL,
    tools=[calculator,age_calculator,weather,mem0_memory],
    system_prompt=prompt,
    callback_handler=stream_callback

)  # Replace this line


# ============================================================
# TODO 5: Interactive chat loop
# ============================================================

print("🤖 Full Agent Ready! Type 'quit' to exit.")
print("Try: 'What's the weather in Delhi and how old is someone born 2000-01-01?'")
print("Try: 'Remember my name is [name]' then 'What's my name?'\n")

while True:
    try:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye! 👋")
            break

        print("\nAgent: ", end="")
        agent(user_input)
        print()

    except KeyboardInterrupt:
        print("\nBye! 👋")
        break

print("\n✅ Challenge 4 complete! 🏆")
