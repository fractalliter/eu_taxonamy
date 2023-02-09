from dataclasses import dataclass
from typing import Optional


@dataclass
class Code:
    nace: str
    id: Optional[str] = None
