from datetime import datetime
from typing import Optional

from ninja import Schema


class ShareCodeSchema(Schema):
    id: int
    code: str
    note: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None


class ShareCodeCreate(Schema):
    note: Optional[str] = None
    expires_at: Optional[datetime] = None
