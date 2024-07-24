import datetime
import uuid


class DomainBase:
    id: uuid.UUID
    created: datetime.datetime

    def __init__(
        self, id: uuid.UUID | None = None, created: datetime.datetime | None = None
    ):
        if id:
            self.id = id
        if created:
            self.created = created
