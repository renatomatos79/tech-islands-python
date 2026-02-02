from mcp.server.fastmcp import FastMCP
from random import choice

mcp = FastMCP("random_name")

@mcp.tool()
def get_random_name(names: list = []) -> str:
    if len(names) > 0:
        return choice(names)
    return choice(["Alice","Bob","Charlie","Diana","Eve","Frank","Grace","Hank","Ivy","Jack"])
