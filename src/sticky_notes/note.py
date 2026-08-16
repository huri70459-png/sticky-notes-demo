from dataclasses import dataclass

@dataclass
class Note:
    id: str
    text: str
    color: str
    pinned: bool = False
    width: int = 200
    height: int = 100
    content: str = ""
    always_on_top: bool = False
    links: list = None
    tags: list = None

    def __post_init__(self):
        if self.links is None:
            self.links = []
        if self.tags is None:
            self.tags = []
