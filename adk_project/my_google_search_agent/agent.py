import os

from google.adk.agents import Agent
from google.adk.tools import google_search


MODEL = os.getenv("MODEL", "gemini-3.5-flash")

root_agent = Agent(
    name="my_google_search_agent",
    model=MODEL,
    description="An agent that answers questions using Google Search grounding.",
    instruction=(
        "You are a helpful agent. Use Google Search when the user asks for "
        "current, time-sensitive, or factual information that may have changed."
    ),
    tools=[google_search],
)
