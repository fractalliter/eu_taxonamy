from dataclasses import dataclass
from typing import Optional


@dataclass
class Sector:
    name: str
    reference: int
    id: Optional[str] = None
