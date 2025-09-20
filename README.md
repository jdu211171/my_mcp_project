# MCP Stock Query System

An intelligent stock data retrieval system built on the Model Context Protocol (MCP) that combines AI-powered query understanding with reliable financial data access. The system uses Google's Gemini AI to interpret natural language queries and automatically selects the appropriate tools to fetch stock market information.

## Features

- 🤖 AI-Powered Query Understanding: Uses Google Gemini to interpret natural language stock queries

- 📊 Dual Data Sources: Primary Yahoo Finance API with CSV fallback for reliability

- 🔄 Automatic Tool Selection: Intelligent mapping of user queries to appropriate stock tools

- 💬 Interactive Chat Interface: Simple command-line interface for natural conversations

- 🛡️ Robust Error Handling: Comprehensive fallback mechanisms and error recovery

- ⚡ Asynchronous Processing: High-performance async operations for better responsiveness

## Architecture

The system consists of two main components:

### MCP Client (mcp_client.py)

- Handles user input and natural language processing

- Connects to the MCP server via stdio communication

- Uses Gemini AI to identify appropriate tools and arguments

- Manages the interactive user session

### MCP Server (mcp_server.py)

- Provides stock data tools through the MCP protocol

- Implements Yahoo Finance API integration with CSV fallback

- Exposes two main tools: get_stock_price and compare_stocks

- Handles data source failover automatically

## Installation

### Prerequisites

- Python 3.10 or higher

- Google AI API key (Gemini)

- Internet connection for Yahoo Finance data

### Setup Steps

1. Clone or download the project files
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Configure environment variables (.env):
```
GEMINI_API_KEY=your_gemini_api_key_here
```
4. Update working directory:
```
cwd="C:/your/project/path"  # Update this path
```
5. Ensure `stocks_data.csv` is present in your working directory. This CSV file serves as a fallback data source when the Yahoo Finance API is unavailable due to network issues, or service outages. The local dataset contains price information for a curated selection of top-performing stocks to provide reliable offline access to essential market data.

## Usage

### Starting the System

1. Run the client:
```
python mcp_client.py
```

2. Enter natural language queries:
```
What is your query? → What's the current price of Apple?
What is your query? → compare stock price of Apple and Microsoft
```

### Example Interactions

#### Single Stock Query:

```
Input: "What's the price of AAPL?"
Output: The current price of AAPL is $150.25 (from Yahoo Finance)
```

#### Stock Comparison:

```
Input: "Compare Apple and Microsoft stocks"
Output: AAPL ($150.25 YF) is lower than MSFT ($380.50 YF).
```

#### Fallback Data:

```
Input: "Get Tesla stock price"
Output: The current price of TSLA is $250.87 (from local data)
```

### File Structure

```
├── mcp_client.py          # Main client application
├── mcp_server.py          # MCP server with stock tools
├── .env                   # Environment variables (API keys)
├── requirements.txt       # Python dependencies
├── stocks_data.csv        # Fallback stock data
└── README.md             # This file
```

## Available Tools

`get_stock_price`

- Purpose: Retrieve current stock price for a single symbol
- Parameters:
```symbol (string): Stock ticker symbol (e.g., "AAPL", "MSFT")```

- Example Usage:
```
"What's Apple's stock price?"
"Get TSLA price"
"Show me Microsoft stock value"
```

`compare_stocks`

- Purpose: Compare prices between two stock symbols
- Parameters:
```
symbol1 (string): First stock ticker symbol
symbol2 (string): Second stock ticker symbol
```
- Example Usage:
```
"Compare Apple and Google stocks"
"Which is higher, MSFT or AAPL?"
"Show me Tesla vs Ford stock prices"
```

## Configuration

### API Keys

Set your Gemini API key in the .env file:

```
GEMINI_API_KEY=your_actual_api_key_here
```

### Working Directory

Update the cwd parameter in mcp_client.py:

```
server_params = StdioServerParameters(
    command="python",
    args=["mcp_server.py"],
    cwd="/path/to/your/project"  # Update this
)
```

### CSV Data Format

The fallback CSV file should follow this structure:

```
symbol,price,last_updated
AAPL,150.25,2024-01-15
MSFT,380.50,2024-01-15
```

## Data Sources

### Primary: Yahoo Finance

- Real-time stock data via yfinance library
- Comprehensive market coverage
- Automatic retry mechanisms

### Fallback: Local CSV

- Offline data access when Yahoo Finance is unavailable
- Customizable stock universe
- Fast local lookups

## Troubleshooting

### Common Issues

#### "TLS connect error" or "OpenSSL invalid library" when accessing Yahoo Finance:

ERROR Failed to get ticker 'AAPL' reason: Failed to perform, curl: (35) TLS connect
error: error:00000000:invalid library (0):OPENSSL_internal:invalid library (0).


**Cause**: This error occurs when your environment has network restrictions, firewall policies, or SSL/TLS configuration issues that prevent secure connections to Yahoo Finance servers.

**Common scenarios**:
- Corporate networks with strict SSL/TLS policies
- Outdated OpenSSL libraries or certificates
- VPN or proxy configurations blocking financial APIs
- Restricted network environments (institutional, educational)

**Solution**: The system automatically falls back to local data (`stocks_data.csv`) when Yahoo Finance is inaccessible. Verify your query symbol exists in the CSV file for successful data retrieval.

**Manual resolution**:
- Update your system's OpenSSL libraries
- Configure proxy settings if behind corporate firewall
- Contact your network administrator for API access permissions
- Ensure `stocks_data.csv` contains the required ticker symbols as backup

#### "Connection error":
- Verify mcp_server.py is in the correct directory
- Check the cwd parameter in mcp_client.py
- Ensure Python is in your system PATH

#### "Could not retrieve price":
- Verify stock symbol is correct
- Check internet connection for Yahoo Finance
- Ensure stocks_data.csv exists and has correct format

#### "API key error":
- Verify GEMINI_API_KEY is set in .env
- Check API key validity and quotas
- Ensure .env file is in the project root

#### Debug Mode

For detailed debugging, check console output which shows:
- Connection status
- Tool identification process
- Data source selection
- Error details

## Dependencies

- mcp[cli]==1.8.1 - Model Context Protocol framework
- yfinance==0.2.61 - Yahoo Finance API wrapper
- google-genai==1.15.0 - Google Gemini AI client
- python-dotenv==1.1.0 - Environment variable management