import datetime
from uuid import UUID


class DomainBase:
    id: UUID
    account_id: UUID
    created: datetime.datetime

    def __init__(
        self,
        account_id: UUID,
        id: UUID | None = None,
        created: datetime.datetime | None = None,
    ):
        if id:
            self.id = id
        self.account_id = account_id
        self.created = (
            created if created else datetime.datetime.now(datetime.timezone.utc)
        )
