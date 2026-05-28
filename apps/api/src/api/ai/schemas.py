from enum import Enum
from pydantic import BaseModel, Field


class Tag(str, Enum):
    SECURITY = "Security"
    PERFORMANCE = "Performance"
    DISRUPTION = "Disruption"
    CRASH = "Crash"
    NETWORK = "Network"
    DOCUMENTATION = "Documentation"
    FEATURE = "Feature"
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    PRODUCT = "Product"
    INTEGRATION = "Integration"
    MARKETING = "Marketing"


class TicketClassification(BaseModel):
    tags: list[Tag] = Field(min_length=1, max_length=5)
    reasoning: str | None = None
