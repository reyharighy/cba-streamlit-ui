# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false

# standard
import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from typing import Any, Literal
from collections.abc import Generator
from time import sleep

# third-party
import streamlit as st
from pydantic import BaseModel, Field
from streamlit.delta_generator import DeltaGenerator

# internal
from .cache import load_infographic
from .runtime import SessionMemory
from infographic import infographic_dir_path

load_dotenv()

AGENT_API_BASE_URL: str | None = os.getenv("AGENT_API_BASE_URL", None)

if AGENT_API_BASE_URL is None:
    raise ValueError("AGENT_API_BASE_URL is not set in the environment variables.")

class ChatHistory(BaseModel):
    """
    Schema for chat history between human and AI.
    """

    turn_num: int = Field(ge=1)
    role: Literal["human", "ai"]
    content: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=datetime.now)

class UserInterface:
    def __init__(self) -> None:
        """
        Initializes the UserInterface with the provided MemoryManager.
        """
        self.session_memory: SessionMemory = SessionMemory()

    def run(self) -> None:
        """
        Runs the user interface, handling session initialization, chat history display, chat input processing, and toast
        messages.
        """
        self.__init_session_and_config()
        self.__display_chat_history()
        self.__process_chat_input()
        self.__show_toast_message()

    def __init_session_and_config(self) -> None:
        """
        Initializes the session state and configures the Streamlit page.
        """
        if st.session_state.get("init_app") is None:
            st.session_state["success_toast"] = False
            st.session_state["error_toast"] = False
            st.session_state["punt_toast"] = False
            st.session_state["punt_response"] = []
            st.session_state["init_app"] = not None
            st.rerun()

        st.set_page_config(
            page_title="CBA - Agentic AI",
            layout="wide",
            initial_sidebar_state="auto",
        )

    def __display_chat_history(self) -> None:
        """
        Displays the chat history from the memory manager.
        """
        chat_history: list[dict[str, Any]] = requests.get(f"{AGENT_API_BASE_URL}/chat/history").json()

        self.session_memory.turn_num = max(ChatHistory.model_validate(chat).turn_num for chat in chat_history) if chat_history else 0

        if self.session_memory.turn_num > 0:
            message_block: list[ChatHistory | str] = []

            for chat in chat_history:
                message_block.append(ChatHistory.model_validate(chat))

                if len(message_block) == 2:
                    self.__render_chat_turn_block(chat_turn=message_block)
                    message_block = []

    def __process_chat_input(self) -> None:
        """
        Processes user chat input and triggers graph invocation.
        """
        if chat_input := st.chat_input("Chat with AI"):
            self.session_memory.chat_input = chat_input
            self.__render_chat_turn_block(on_processing_request=True)
            st.rerun()

    def __render_chat_turn_block(
        self, on_processing_request: bool = False, chat_turn: list[ChatHistory | str] = []
    ) -> None:
        """
        Renders a chat turn block in the user interface.
        """
        st.divider()

        with st.expander("Click to toggle cell", expanded=True):
            with st.container(border=True):
                st.badge("Your Prompt", color="orange")

                self.__render_turn_element(
                    input_type=True,
                    on_processing_request=on_processing_request,
                    turn_element=chat_turn[0] if not on_processing_request else None,
                )

            st.badge("System Response", color="blue")

            self.__render_turn_element(
                input_type=False,
                on_processing_request=on_processing_request,
                turn_element=chat_turn[1] if not on_processing_request else None,
            )

            if chat_turn and isinstance(chat_turn[-1], ChatHistory):
                self.__render_infographic_turn_block(chat_turn[-1].turn_num)

    def __render_turn_element(
        self, input_type: bool, on_processing_request: bool, turn_element: ChatHistory | str | None
    ) -> None:
        """
        Renders a turn element in the user interface.
        """
        if on_processing_request:
            st.write(self.session_memory.chat_input) if input_type else self.__graph_invocation()
        elif isinstance(turn_element, ChatHistory):
            st.write(turn_element.content)
        elif isinstance(turn_element, str):
            st.write(turn_element)
        else:
            raise ValueError("'turn_element' must not be None when 'on_processing_request' is False")

    def __render_infographic_turn_block(self, turn_num: int) -> None:
        """
        Renders the infographic turn block for the specified turn number.
        """
        infographic_object_dir_path: Path = infographic_dir_path / f"turn_num_{turn_num}"

        if infographic_object_dir_path.exists():
            infographic_object_file_path: Path = infographic_object_dir_path / "infographic.py"
            loader, module = load_infographic(infographic_object_file_path)

            if loader and module:
                loader.exec_module(module)

    def __graph_invocation(self) -> None:
        """
        Invokes the state graph and streams the output to the user interface.
        """
        status_box: DeltaGenerator = st.status("Analyzing your intent", expanded=True)
        stream_placeholder: DeltaGenerator = status_box.empty()

        with requests.post(
            f"{AGENT_API_BASE_URL}/agent/stream",
            json={"input": self.session_memory.chat_input},
            stream=True,
        ) as response:
            try:
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith("data: "):
                        payload_type = json.loads(line.removeprefix("data: ")).get("type")

                        if payload_type == "error":
                            raise Exception(json.loads(line.removeprefix("data: ")).get("message"))

                        if payload_type == "complete":
                            break

                        payload_data = json.loads(line.removeprefix("data: ")).get("data")

                        for key, value in payload_data.items():
                            if ui_payload := value.get("ui_payload"):
                                status_box.update(label=ui_payload)

                            if key == "summarization":
                                st.session_state["success_toast"] = True
                                continue

                            if key.endswith("_response"):
                                self.session_memory.chat_output = value.get("messages")[-1].get("content")

                                if key.startswith("punt"):
                                    st.session_state["punt_response"].append(self.session_memory.chat_input)
                                    st.session_state["punt_response"].append(self.session_memory.chat_output)
                                    st.session_state["punt_toast"] = True

                                stream_placeholder.write(self.__stream_generator)
                                continue

                            if key.endswith("_result") or key.endswith("_execution") or key.startswith("context"):
                                continue

                            if rationale := value.get(key).get("rationale"):
                                self.session_memory.thinking = rationale
                                stream_placeholder.write(self.__stream_generator)

            except Exception as e:
                st.session_state["error_toast"] = True
                st.error(f"Graph execution failed: {e}")

    def __stream_generator(self) -> Generator[str, None, None]:
        """
        Generator to stream the thinking or chat output word by word.
        """
        if self.session_memory.thinking:
            for word in str(self.session_memory.thinking).split(" "):
                yield word + " "
                sleep(0.01)

            self.session_memory.thinking = None

        elif self.session_memory.chat_output:
            for word in str(self.session_memory.chat_output).split(" "):
                yield word + " "
                sleep(0.01)

    def __show_toast_message(self) -> None:
        """
        Shows toast messages based on the session state.
        """
        if st.session_state["success_toast"]:
            st.session_state["success_toast"] = False

            st.toast(
                body="###### **Your request is completed.**",
                duration="long",
            )

        if st.session_state["punt_toast"]:
            self.__render_chat_turn_block(chat_turn=st.session_state["punt_response"])
            st.session_state["punt_toast"] = False
            st.session_state["punt_response"] = []

            st.toast(
                body="###### **Your request is out of business analytics domain. This chat turn will not be persisted.**",
                duration="long",
            )

            sleep(10)
            st.rerun()

        if st.session_state["error_toast"]:
            st.session_state["error_toast"] = False

            st.toast(
                body="###### **System fails to process your request. Please try again.**",
                duration="long",
            )