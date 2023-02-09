from dataclasses import dataclass
from typing import Optional


@dataclass
class Criteria:
    description: str
    id: Optional[str] = None
