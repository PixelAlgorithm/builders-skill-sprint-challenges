"""
Bedrock Cost Guardian — smarter AWS/Bedrock cost estimation agent.
"""

from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters, stdio_client

cost_mcp = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="uvx", args=["awslabs.aws-pricing-mcp-server@latest"])
))

with cost_mcp:
    tools = cost_mcp.list_tools_sync()

    agent = Agent(
        model="us.amazon.nova-pro-v1:0",
        tools=tools,
        system_prompt=(
            "You are Bedrock Cost Guardian, an AWS cost estimation expert.\n\n"
            "WORKFLOW for any Bedrock model pricing question:\n"
            "1. Service code for Bedrock pricing is ALWAYS 'AmazonBedrock' — "
            "skip get_pricing_service_codes for Bedrock queries.\n"
            "2. Call get_pricing_attribute_values for the 'model' attribute on "
            "AmazonBedrock to get the list of model IDs AWS actually bills for "
            "in the relevant region.\n"
            "3. Match the user's requested model name against that REAL list. "
            "Use fuzzy/partial matching (ignore version suffixes, dashes, case).\n"
            "4. If you find a clear match, quote that model's actual price.\n"
            "5. If you find NO match or multiple plausible matches, tell the "
            "user exactly which model IDs ARE available (from the tool output) "
            "and ask them to confirm — do NOT guess or invent a price.\n"
            "6. NEVER state a model exists or has a price unless it appeared in "
            "the tool's actual output for this session.\n\n"
            "BEDROCK COST CALCULATION:\n"
            "- Always fetch and show BOTH input and output token prices.\n"
            "- If token volume given, compute: "
            "(input_tokens/1000 * input_price) + (output_tokens/1000 * output_price). "
            "If input/output split isn't specified, assume 80/20 and state this.\n\n"
            "OUTPUT FORMAT:\n"
            "1. Markdown table: Service | Configuration | Est. Monthly Cost (USD) | Notes\n"
            "2. '💡 Cheaper Alternative' — only models confirmed via the pricing "
            "tool, with real price comparison.\n"
            "3. 'Session Total Estimate' — running total, updated on request.\n"
            "4. If ambiguous, ask ONE clarifying question instead of guessing."
        ),
    )

    print("💰 Bedrock Cost Guardian — ask me about AWS costs (type 'exit' to quit)")
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Goodbye! Keep your AWS bills low!")
                break
            if not user_input:
                continue
            response = agent(user_input)
            print(f"\nGuardian: {response}")
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Keep your AWS bills low!")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}")