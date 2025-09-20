from mcp.server.fastmcp import FastMCP
import yfinance as yf

mcp = FastMCP("Stock Server")


@mcp.tool(name="get_stock_price")
def get_stock_price(symbol: str) -> str:
    """Get the current stock price for a given symbol."""
    try:
        ticker = yf.Ticker(symbol)

        # Get today's data
        data = ticker.history(period="1d")

        if not data.empty:
            price = float(data['Close'].iloc[-1])
            return f"The current price of {symbol} is ${price:.2f}"
        else:
            info = ticker.info
            price = info.get('regularMarketPrice')
            if isinstance(price, (int, float)):
                return f"The current price of {symbol} is ${float(price):.2f}"
            return f"Could not retrieve price for symbol: {symbol}. Market may be closed."

    except Exception as e:
        return f"An error occurred while fetching the stock price: {str(e)}"
            

@mcp.tool()
def compare_stocks(symbol1: str, symbol2: str) -> str:
    """Compare two stocks based on their current prices."""
    try:
        ticker1 = yf.Ticker(symbol1)
        ticker2 = yf.Ticker(symbol2)

        data1 = ticker1.history(period="1d")
        data2 = ticker2.history(period="1d")

        if not data1.empty and not data2.empty:
            price1 = float(data1['Close'].iloc[-1])
            price2 = float(data2['Close'].iloc[-1])
        else:
            info1 = ticker1.info
            info2 = ticker2.info
            p1 = info1.get('regularMarketPrice')
            p2 = info2.get('regularMarketPrice')
            if not isinstance(p1, (int, float)) or not isinstance(p2, (int, float)):
                return "Could not retrieve prices for comparison."
            price1 = float(p1)
            price2 = float(p2)

            
        if price1 > price2:
            return f"{symbol1} is higher than {symbol2}: ${price1:.2f} vs ${price2:.2f}"
        elif price1 < price2:
            return f"{symbol2} is higher than {symbol1}: ${price2:.2f} vs ${price1:.2f}"
        else:
            return f"{symbol1} and {symbol2} are equal at ${price1:.2f}"

    except Exception as e:
        return f"An error occurred while comparing the stock prices: {str(e)}"
    

if __name__ == "__main__":
    mcp.run()
