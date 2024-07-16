import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DomainBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    account_id: UUID
    created_at: datetime.datetime
