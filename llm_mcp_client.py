"""
Interactive LLM client that pulls tool definitions from the MCP server and
lets you test them via the OpenAI chat completions API.
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Union

from fastmcp import Client
from openai import OpenAI
import yaml

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

CONFIG_PATH = Path("config.yml")
DEFAULT_MODEL = "gpt-5.1"
EXIT_WORDS = {"exit", "quit", "q"}


def load_api_key() -> str:
    """Load OPENAI_API_KEY from .env or the current environment."""
    if load_dotenv is not None:
        load_dotenv()
    else:
        _fallback_load_env_file()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to a .env file or export it before running."
        )
    return api_key


def _fallback_load_env_file() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_config() -> Dict[str, Any]:
    """Load configuration from config.yml (or return an empty dict if missing)."""
    if not CONFIG_PATH.exists():
        return {}
    try:
        data = yaml.safe_load(CONFIG_PATH.read_text()) or {}
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        # Keep the client usable even if config is malformed.
        return {}


def resolve_mcp_transport(config: Dict[str, Any]) -> Union[str, Path]:
    """
    Resolve the MCP server target.
    Prefer an HTTP URL (realistic deployment), fall back to a local path for stdio.
    """
    url = config.get("mcp_server_url")
    if isinstance(url, str) and url.strip():
        return url.strip()

    path_value = config.get("mcp_server_path") or "globalapi_mcp_server.py"
    mcp_path = Path(path_value).expanduser().resolve()
    if not mcp_path.exists():
        raise FileNotFoundError(
            f"MCP server path not found: {mcp_path}. "
            "Update config.yml:mcp_server_path or set mcp_server_url."
        )
    return mcp_path


async def build_openai_tools(mcp_client: Client) -> List[Dict[str, Any]]:
    """Fetch tool metadata from the MCP server and adapt it for OpenAI."""
    tools = await mcp_client.list_tools()
    openai_tools: List[Dict[str, Any]] = []
    print("\nFetched tools from MCP server:")
    for tool in tools:
        schema = tool.inputSchema or {"type": "object", "properties": {}}
        openai_tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": schema,
                },
            }
        )

        required = ", ".join(schema.get("required", [])) if isinstance(schema, dict) else ""
        print(f"- {tool.name} (requires: {required or 'none'})")
    return openai_tools


async def call_mcp_tool(mcp_client: Client, name: str, arguments: Dict[str, Any]) -> str:
    """Call a tool on the MCP server and return a JSON string for the chat history."""
    result = await mcp_client.call_tool(name=name, arguments=arguments or {})

    if result.data is not None:
        payload: Any = result.data
    elif result.structured_content is not None:
        payload = result.structured_content
    elif result.content:
        payload = [getattr(item, "text", str(item)) for item in result.content]
    else:
        payload = "Tool returned no content."

    return json.dumps(payload, ensure_ascii=False, default=str)


async def run_conversation_turn(
    llm: OpenAI,
    mcp_client: Client,
    messages: List[Dict[str, Any]],
    tools: List[Dict[str, Any]],
    model_name: str,
) -> None:
    """Send the conversation to the LLM, handle tool calls, and print the reply."""
    while True:
        completion = llm.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        message = completion.choices[0].message

        tool_calls = message.tool_calls or []
        assistant_content = message.content or ""
        if tool_calls:
            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in tool_calls
                    ],
                }
            )

            for tc in tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                print(f"\n> Calling tool '{tc.function.name}' with {args}")
                try:
                    tool_response = await call_mcp_tool(
                        mcp_client, tc.function.name, args
                    )
                except Exception as exc:  # pylint: disable=broad-except
                    tool_response = f"Error calling tool {tc.function.name}: {exc}"
                    print(tool_response)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": tool_response,
                    }
                )
            continue

        messages.append({"role": "assistant", "content": assistant_content})
        print(f"\nAssistant: {assistant_content}\n")
        return


async def main() -> None:
    api_key = load_api_key()
    config = load_config()
    model_name = config.get("openai_model") or DEFAULT_MODEL
    mcp_transport = resolve_mcp_transport(config)

    llm = OpenAI(api_key=api_key)

    print("Starting MCP client...")
    print(f"Using OpenAI model: {model_name}")
    print(f"MCP target: {mcp_transport}")
    async with Client(mcp_transport) as mcp_client:
        openai_tools = await build_openai_tools(mcp_client)

        print("\nAsk a question to test the tools. Type 'exit' to quit.")
        messages: List[Dict[str, Any]] = []
        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in EXIT_WORDS:
                print("Goodbye.")
                break
            messages.append({"role": "user", "content": user_input})
            await run_conversation_turn(
                llm, mcp_client, messages, openai_tools, model_name
            )


if __name__ == "__main__":
    asyncio.run(main())
