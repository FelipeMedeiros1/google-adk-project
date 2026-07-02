from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from my_google_search_agent.agent import root_agent


APP_NAME = "app_agent"
USER_ID = "user"


def main():
    session_service = InMemorySessionService()

    runner = InMemoryRunner(
        agent=root_agent,
        app_name=APP_NAME
    )

    session = session_service.create_session_sync(
        app_name=APP_NAME,
        user_id=USER_ID
    )

    message = "What is the capital of France?"

    print(f"** User says: {message}")

    for event in runner.run(
        user_id=USER_ID,
        session_id=session.id,
        new_message=Content(
            role="user",
            parts=[Part(text=message)]
        )
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    print(part.text)


if __name__ == "__main__":
    main()