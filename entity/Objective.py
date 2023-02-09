from dataclasses import dataclass
from typing import Optional


@dataclass
class Objective:
    name: str
    long_name: str
    key: str
    id: Optional[str] = None
