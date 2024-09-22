from typing import Any, Optional

from pydantic import BaseModel


class FilterUser(BaseModel):
    unsafe_metadata_role: str


class UserModel(BaseModel):
    id: str
    public_metadata: dict[str, Any]
    private_metadata: Optional[dict[str, Any]]
    unsafe_metadata: dict[str, Any]
    email_address: Optional[str]
    phone_number: Optional[str]
    image_url: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    last_active_at: Optional[int]
    created_at: int
