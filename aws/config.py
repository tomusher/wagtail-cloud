from dataclasses import dataclass
from enum import Enum


@dataclass
class StackConfig:
    class Scale(Enum):
        TINY = "tiny"
        SMALL = "small"
        BIG = "big"
        HUGE = "huge"

    name: str
    region: str
    scale: Scale
    domain: str
    media_domain: str
