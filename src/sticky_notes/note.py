from dataclasses import dataclass

@dataclass
class Note:
    id: str
    text: str
    color: str
    pinned: bool = False
    width: int = 200
    height: int = 100
