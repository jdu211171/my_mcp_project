# Python MCP Stocks Tools (FastMCP server + CLI client)

Small, focused example of using the Model Context Protocol (MCP) to wire an AI
assistant to real tools. The FastMCP server exposes stock tools and the Python
CLI client asks Gemini to pick the right tool and arguments, then calls it over
stdio.

Key features
- Gemini‑driven tool selection from plain‑English queries
- Yahoo Finance primary data with CSV fallback for reliability
- Simple stdio wiring between client and server (no sockets to configure)
- Minimal dependencies, clear structure, and deterministic prompts

--------------------------------------------------------------------------------

## Quickstart

Prereqs
- Python 3.11+ (developed with 3.13)
- A Gemini API key in `.env` as `GEMINI_API_KEY=...`

Setup
```
python -m venv venv
source venv/bin/activate        # Windows: .\\venv\\Scripts\\activate
pip install -U pip
pip install -r requirements.txt
```

Run
- Server (direct): `python mcp_server.py`
- Client (spawns server via stdio): `python mcp_client.py`

Try a query
```
What is your query? → What's the current price of AAPL?
What is your query? → Compare MSFT and AAPL
```

--------------------------------------------------------------------------------

## Project Structure
```
├── mcp_server.py      # FastMCP server exposing tools
├── mcp_client.py      # CLI: lists tools, asks Gemini, calls tool
├── requirements.txt   # Pinned runtime deps
├── .env               # Local secrets (e.g., GEMINI_API_KEY)
├── stocks_data.csv    # Optional CSV fallback data
└── README.md
```

--------------------------------------------------------------------------------

## How It Works

Flow
1) `mcp_client.py` lists server tools over MCP stdio.
2) It prompts Gemini with a deterministic, JSON‑only instruction to choose a
   tool and arguments.
3) The client calls the chosen tool via MCP and prints the result.

Data sources
- Primary: Yahoo Finance via `yfinance`
- Fallback: `stocks_data.csv` with schema `symbol,price,last_updated`

Update working directory
- The client launches the server with `cwd` set in `mcp_client.py`.
- Ensure it points to your project path if you run from elsewhere.

--------------------------------------------------------------------------------

## Tools (Server)

`get_stock_price(symbol: str) -> str`
- Returns the current price using Yahoo Finance, falling back to CSV when
  needed.
- Example queries: “What’s Apple’s stock price?”, “Get TSLA price”.

`compare_stocks(symbol1: str, symbol2: str) -> str`
- Compares two symbols and reports which is higher (with source hints).
- Example queries: “Compare MSFT and AAPL”, “Tesla vs Ford prices”.

CSV format
```
symbol,price,last_updated
AAPL,150.25,2024-01-15
MSFT,380.50,2024-01-15
```

--------------------------------------------------------------------------------

## Configuration

.env
```
GEMINI_API_KEY=your_api_key_here
```

Deterministic prompts
- `fetch_tool_identifier_prompt()` expects JSON‑only model output.
- The client strips code fences and parses JSON. If `arguments` arrives as a
  string (e.g., "symbol, AAPL"), the client coerces it into a dict.

Network behavior
- Avoid tight polling. External calls go to yfinance and Gemini; failures
  fall back to CSV where possible.

--------------------------------------------------------------------------------

## Development

Lint/format (optional)
```
pip install ruff black
ruff check .
black .
```

Coding style
- Python 3.11+, 4‑space indent, ~88‑char lines.
- Public functions use type hints and short docstrings.
- Names: modules/functions `snake_case`, classes `PascalCase`, constants
  `UPPER_CASE`.
- MCP tools use `@mcp.tool(...)` and return concise text.

--------------------------------------------------------------------------------

## Testing

```
pip install pytest pytest-asyncio
pytest -q
```

Coverage (optional)
```
pip install pytest-cov
pytest --cov=mcp_server --cov=mcp_client
```

--------------------------------------------------------------------------------

## Troubleshooting

Gemini/API key
- Ensure `.env` contains `GEMINI_API_KEY` and the key is valid.

Server launch path
- If the client can’t connect, verify the `cwd` in `mcp_client.py` matches your
  project directory.

Yahoo Finance/SSL or network errors
- In restricted or flaky networks, yfinance may fail TLS/SSL. The server will
  fall back to `stocks_data.csv`. Ensure the required symbols exist in the CSV.

No price found
- Confirm the ticker symbol and that either yfinance is reachable or the CSV
  has a row for the symbol.

--------------------------------------------------------------------------------

## Contributing

- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`.
- Keep PRs small and focused. Include what/why, how to test (commands and
  expected output), and screenshots/terminal snippets when useful. Link issues
  like `#12` when applicable.
- Update this README for behavior changes; add migration notes if prompts/APIs
  change.

--------------------------------------------------------------------------------

## Security Notes

- Do not commit secrets. Keep them in `.env`.
- Minimize logging; never print secrets.
- External calls hit third‑party APIs; handle errors clearly and back off when
  failing.

Disclaimer
- Provided for educational/demo purposes only. Not financial advice.
