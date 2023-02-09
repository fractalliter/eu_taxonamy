from dataclasses import dataclass
from typing import Optional
from .Sector import Sector
from .Code import Code


@dataclass
class Activity:
    name: str
    description: str
    reference: float
    sector: Sector
    nace_codes: Code
    id: Optional[str] = None
