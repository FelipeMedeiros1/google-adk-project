import os

from google.adk.agents import Agent


MODEL = os.getenv("MODEL", "gemini-3.5-flash")

root_agent = Agent(
    name="llm_auditor",
    model=MODEL,
    description="An auditor agent that checks factual claims and corrects them.",
    instruction=(
        "You are a careful factual auditor. Review the user's statement, "
        "identify whether it is accurate, and provide a concise correction "
        "when it is false."
    ),
)
