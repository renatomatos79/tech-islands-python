from mcp.server.fastmcp import FastMCP
from random import choice
import os

# app port number, if not set, uses 8000
port = int(os.environ.get("APP_PORT", 8000))

# Initialize FastMCP server
mcp = FastMCP(
    "ramdom_name", host="0.0.0.0", port=port
)  

@mcp.tool()
def get_random_name(names: list = []) -> str:
    """Gets a random peoples names. The names are stored in a local array
    args:
       names:the user can pass in a list of names to choose from, or it will default to a predefined list.
    """

    # If names is provided and not empty, use it; otherwise use default list
    if len(names) > 0:
        return choice(names)
    else:
        # Use default list of names
        default_names = [
            "Alice",
            "Bob",
            "Charlie",
            "Diana",
            "Eve",
            "Frank",
            "Grace",
            "Hank",
            "Ivy",
            "Jack",
        ]
        return choice(default_names)

 #

if __name__ == "__main__":
    mcp.run()