import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

def fetch_tool_identifier_prompt():
    tool_identifier_prompt = """

        You have been given access to the below MCP Server Tools

        {tools_description}

        You must identify the appropriate tool only from the above tools required to resolve the user query along with the arguments,

        {user_query}

        Your output should be in json like below

        {{
            user_query: "User Query",
            tool_identified: "Tool Name",
            arguments: "arg1, arg2"
        }}

        Example:

        User Query: What is the weather in Bengaluru?

        Your Response:
        {{
            user_query: "What is the weather in Bengaluru?"
            tool_identified: "get_weather"
            arguments: {{"location":"BLR"}}
        }}

        """
    return tool_identifier_prompt

async def generate_response(user_query: str, tools_description: str):
    """
    Generate AI response to identify appropriate tool for user query.
    
    This function uses Google's Gemini AI model to analyze the user query against
    available MCP server tools and returns the identified tool with its arguments.
    
    Args:
        user_query (str): The user's input query that needs to be resolved
        tools_description (str): Description of available MCP server tools
        
    Returns:
        dict: A dictionary containing:
            - user_query: The original user query
            - tool_identified: Name of the identified tool
            - arguments: Dictionary of arguments for the tool
            
    Raises:
        Exception: If API key is missing or AI model fails to respond
        json.JSONDecodeError: If the AI response cannot be parsed as JSON
        
    Example:
        >>> await generate_response("What's the weather?", "get_weather: Gets weather data")
        {
            "user_query": "What's the weather?",
            "tool_identified": "get_weather",
            "arguments": {"location": "default"}
        }
    """
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    tool_identifier_prompt = fetch_tool_identifier_prompt()
    tool_identifier_prompt = tool_identifier_prompt.format(user_query=user_query, tools_description=tools_description)

    response = client.models.generate_content(
        model='gemini-2.0-flash-001', 
        contents=tool_identifier_prompt
    )
    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```","")
    data = json.loads(raw)

    if isinstance(data["arguments"], str):
        args_list = [arg.strip() for arg in data["arguments"].split(",")]
        data["arguments"] = {args_list[0]: args_list[1]} if len(args_list) > 1 else {args_list[0]: True}

    return data
    
async def main(user_input: str):
    """
    Main function to handle MCP client session and tool execution.
    
    This function establishes a connection to the MCP server, initializes a session,
    lists available tools, identifies the appropriate tool using AI, and executes
    the identified tool with the provided arguments.
    
    Args:
        user_input (str): The user's query to be processed
        
    Returns:
        None: Prints results to console
        
    Raises:
        Exception: Various exceptions related to MCP server connection,
                  session initialization, or tool execution
                  
    Note:
        The server parameters are hardcoded and should be configured for your
        specific environment. Update the 'cwd' parameter to match your project path.
        
    Example:
        >>> await main("What is the weather in New York?")
        # Connects to MCP server, identifies weather tool, executes it
    """
    print("-"*50)
    print("The User Input is : ", user_input)
    server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"],
            cwd="/home/user/Development/my_mcp_project" #Configure your current working directory
        )
    try:
        async with stdio_client(server_params) as (read, write):
            print("Connection established, creating session...")
            try:
                async with ClientSession(read, write) as session:
                    print("[agent] Session created, initializing...")
                    try:
                        await session.initialize()
                        print("[agent] MCP session initialized")

                        tools = await session.list_tools()
                        tools_description = ""
                        for each_tool in tools.tools:
                            current_tool_description = "Tool - " + each_tool.name + ":" + "\n"
                            current_tool_description += each_tool.description + "\n"
                            tools_description +=  current_tool_description + "\n"

                        request_json = await generate_response(user_query=user_input, tools_description=tools_description)
                        print(f"To execute the User Query: {user_input} - The Identified tool is {request_json['tool_identified']}, and the parameters required are {request_json['arguments']}")
                        response = await session.call_tool(request_json["tool_identified"], arguments=request_json["arguments"])
                        print(f"{response.content[0].text}")
                        print("-"*50)
                        print("\n\n")
                    except Exception as e:
                            print(f"[agent] Session initialization error: {str(e)}")
            except Exception as e:
                    print(f"[agent] Session creation error: {str(e)}")
    except Exception as e:
            print(f"[agent] Connection error: {str(e)}")

if __name__ == "__main__":
    """
    Entry point for the application.
    
    Runs an interactive loop that continuously prompts the user for queries
    and processes them using the MCP client system. Each query is processed
    asynchronously through the main() function.
    
    Usage:
        Run this script directly to start the interactive query loop.
        Type your queries when prompted and press Enter to process them.
        Use Ctrl+C to exit the loop.
        
    Example:
        $ python mcp_client.py
        What is your query? → What's the weather in London?
        # Processes the query and displays results
        What is your query? → 
    """
    while True:
        query = input("What is your query? → ")
        asyncio.run(main(query))
