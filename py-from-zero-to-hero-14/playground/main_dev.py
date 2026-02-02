from mcp.server.fastmcp import FastMCP
from random import choice

mcp = FastMCP("random_name")

@mcp.tool()
def get_random_name(names: list = []) -> str:
    """Gets a random peoples names. The names are stored in a local array
    args:
       names:the user can pass in a list of names to choose from, or it will default to a predefined list.
    """
    if len(names) > 0:
        return choice(names)
    return choice(["Alice","Bob","Charlie","Diana","Eve","Frank","Grace","Hank","Ivy","Jack"])
