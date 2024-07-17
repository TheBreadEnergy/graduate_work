from typing import Any

from pydantic import BaseModel


class EventSchema(BaseModel):
    type: str
    event: str
    object: dict[str, Any]
