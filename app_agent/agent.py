import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from my_google_search_agent.agent import root_agent


if __name__ == "__main__":
    from google.adk.runners import InMemoryRunner
    from google.genai.types import Content, Part

    user_id = "user"
    message = "What is the capital of France?"
    runner = InMemoryRunner(agent=root_agent, app_name="app_agent")
    session = runner.session_service.create_session_sync(
        app_name="app_agent",
        user_id=user_id,
    )

    print(f"User says: {message}")
    for event in runner.run(
        user_id=user_id,
        session_id=session.id,
        new_message=Content(role="user", parts=[Part(text=message)]),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)
