import os
from fastmcp import FastMCP
from random import choice

port = int(os.environ.get("APP_PORT", 8000))

mcp = FastMCP("random_name")

@mcp.tool
def get_random_name(names: list = []) -> str:
    if len(names)  > 0:
        return choice(names)
    return choice(["Alice","Bob","Charlie","Diana","Eve","Frank","Grace","Hank","Ivy","Jack"])

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=port, path="/mcp")
