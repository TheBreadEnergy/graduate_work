from pydantic import UUID4, BaseModel


class NotificationMessage(BaseModel):
    user_id: UUID4
    subscription_id: UUID4
    message: str
