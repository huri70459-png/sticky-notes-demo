from dataclasses import dataclass

@dataclass
class Note:
    id: str
    text: str
    color: str
    pinned: bool = False
