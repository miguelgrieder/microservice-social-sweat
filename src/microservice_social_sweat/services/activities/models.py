from typing import Optional

from pydantic import BaseModel


class Filter(BaseModel):
    activity_id: Optional[int]
