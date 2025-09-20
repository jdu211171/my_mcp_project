import asyncio
import json
import os
import ast
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from google import genai
from dotenv import load_dotenv

load_dotenv()

def fetch_tool_identifier_prompt():
    tool_identifier_prompt = """
    You have been given access to the below MCP Server Tools

    {tools_description}

    You must identify the appropriate tool only from the above tools required to resolve the user query with the arguments,

    {user_query}

    Your output should be in json like below format:

    {{
        user_query: "User Query",
        tool_identified: "Tool Name",
        arguments: "arg1, arg2, ... "
    }}

    Example:

    User Query: What is the weather in New York City?

    Your Output:
    {{
        user_query: "What is the weather in New York City?",
        tool_identified: "get_weather",
        arguments: "{{'location': 'New York City'}}"
    }}

    """
    return tool_identifier_prompt

def _safe_parse_arguments(val: object) -> dict:
    """Best-effort parsing of tool arguments into a dict.

    Accepts dicts directly, JSON strings, or Python-literal-like strings.
    Returns {} on failure.
    """
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return {}
        # Try JSON first
        try:
            parsed = json.loads(s)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
        # Try Python literal (e.g. {'symbol': 'AAPL'})
        try:
            parsed = ast.literal_eval(s)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
    return {}


async def generate_response(user_query: str, tools_description: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    tool_identifier_prompt = fetch_tool_identifier_prompt()
    tool_identifier_prompt = tool_identifier_prompt.format(
        user_query=user_query, tools_description=tools_description
    )

    chat = client.chats.create(model="gemini-2.0-flash-001")
    response = chat.send_message(tool_identifier_prompt)

    raw = (response.text or "").strip()
    raw = raw.replace("```json", "").replace("```", "")
    try:
        data = json.loads(raw)
    except Exception:
        # Fall back to a minimal, no-op response to avoid crashing
        return {"user_query": user_query, "tool_identified": None, "arguments": {}}

    # Normalize arguments into a dict
    data["arguments"] = _safe_parse_arguments(data.get("arguments", {}))
    return data

async def main(user_input: str):
    print("The User Query is:", user_input)
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
        cwd=".",
    )
    try:
        async with stdio_client(server_params) as (read, write):
            print("Connection established, initializing session...")
            try:
                async with ClientSession(read, write) as session:
                    # Important: initialize before sending any requests
                    await session.initialize()
                    print("Session initialized.")
                    try:
                        tools_result = await session.list_tools()
                        tools = tools_result.tools
                        tools_description = ""
                        for each_tool in tools:
                            desc = each_tool.description or ""
                            tools_description += f"Tool - {each_tool.name}: {desc}\n\n"

                        request_json = await generate_response(
                            user_query=user_input, tools_description=tools_description
                        )

                        tool_name = request_json.get("tool_identified")
                        arguments = request_json.get("arguments", {})

                        # Validate tool name against listed tools
                        tool_names = {t.name for t in tools}
                        if not tool_name or tool_name not in tool_names:
                            print(
                                "[agent] No valid tool identified for this query."
                            )
                            return

                        response = await session.call_tool(tool_name, arguments=arguments)
                        if response.isError:
                            print("[agent] Tool error returned by server.")
                        else:
                            if response.content and response.content[0].type == "text":
                                print(response.content[0].text)
                            else:
                                print("[agent] Tool returned no text content.")
                    except Exception as e:
                        print(f"[agent] Tool call error: {str(e)}")
            except Exception as e:
                print(f"[agent] Session error: {str(e)}")
    except Exception as e:
        print(f"[agent] Session error: {str(e)}")

if __name__ == "__main__":
    while True:
        query = input("Enter your query (or 'exit' to quit): ")
        if query.lower() == "exit":
            break
        asyncio.run(main(query))
