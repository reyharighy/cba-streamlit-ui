# standard
from dataclasses import dataclass


@dataclass
class SessionMemory:
    """
    Dataclass to hold session memory information.
    """

    turn_num: int = 0
    chat_input: str | None = None
    chat_output: str | None = None
    thinking: str | None = None
