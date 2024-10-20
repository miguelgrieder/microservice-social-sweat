import logging
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)

from microservice_social_sweat.services.activities.models import SportType

USER_ID_REGEX = r".*"
PHONE_NUMBER_REGEX = r"^\+[1-9]\d{1,14}$"
BIRTH_DATE_REGEX = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"


class UserSocialMedias(BaseModel):
    user_youtube: Optional[str] = Field(None, max_length=100)
    user_instagram: Optional[str] = Field(None, max_length=100)
    user_facebook: Optional[str] = Field(None, max_length=100)
    user_tiktok: Optional[str] = Field(None, max_length=100)
    user_strava: Optional[str] = Field(None, max_length=100)
    user_phone: Optional[str] = Field(None, pattern=PHONE_NUMBER_REGEX, max_length=16)
    use_phone: Optional[bool] = None
    use_sms: Optional[bool] = None
    use_whatsapp: Optional[bool] = None

    @field_validator("user_phone", mode="before")
    def add_plus_to_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith("+"):
            v = f"+{v}"  # Add the '+' if it's missing
        return v


class UserMetrics(BaseModel):
    activities_created: int = Field(0, ge=0)
    activities_participated: int = Field(0, ge=0)
    activities_participating: int = Field(0, ge=0)


class Role(str, Enum):
    coach = "coach"
    user = "user"
    company = "company"


class FilterUserInput(BaseModel):
    role: Optional[Role] = None
    id: Optional[str] = Field(None, pattern=USER_ID_REGEX)
    username: Optional[str] = Field(None, max_length=50)
    sport_type: Optional[SportType] = None


class UserMetadata(BaseModel):
    role: Role
    sports: list[SportType] = Field(default_factory=list)
    birth_date: Optional[str] = Field(None, pattern=BIRTH_DATE_REGEX)
    user_social_medias: UserSocialMedias = Field(default_factory=UserSocialMedias)
    profile_description: Optional[str] = Field(None, max_length=500)
    user_metrics: UserMetrics = Field(default_factory=UserMetrics)

    @field_validator("sports")
    def validate_sports(cls, v: list[SportType]) -> list[SportType]:
        if len(v) > 10:
            raise ValueError("A maximum of 10 sports can be specified.")
        return v


class UserModel(BaseModel):
    id: str = Field(..., pattern=USER_ID_REGEX)
    user_metadata: UserMetadata
    email_address: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, pattern=PHONE_NUMBER_REGEX)
    image_url: Optional[str] = None
    username: Optional[str] = Field(None, max_length=50)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    last_active_at: Optional[int] = Field(None, ge=0)
    created_at: int = Field(..., ge=0)

    @field_validator("phone_number", mode="before")
    def add_plus_to_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith("+"):
            v = f"+{v}"  # Add the '+' if it's missing
        return v

    @staticmethod
    def from_clerk_user_request(user: dict[str, Any]) -> "UserModel":
        unsafe_metadata = user.get("unsafe_metadata", {})

        role = unsafe_metadata.get("role")
        sports = unsafe_metadata.get("sports", [])
        birth_date = unsafe_metadata.get("birth_date")
        profile_description = unsafe_metadata.get("profile_description")

        user_social_medias_data = unsafe_metadata.get("user_social_medias", {})
        user_social_medias = UserSocialMedias(**user_social_medias_data)

        user_metadata = UserMetadata(
            role=role,
            sports=sports,
            birth_date=birth_date,
            profile_description=profile_description,
            user_social_medias=user_social_medias,
        )

        return UserModel(
            id=user["id"],
            user_metadata=user_metadata,
            email_address=(
                user.get("email_addresses", [{}])[0].get("email_address")
                if user.get("email_addresses")
                else None
            ),
            phone_number=(
                user.get("phone_numbers", [{}])[0].get("phone_number")
                if user.get("phone_numbers")
                else None
            ),
            image_url=user.get("image_url"),
            username=user.get("username"),
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            last_active_at=user.get("last_active_at"),
            created_at=user.get("created_at"),
        )


class UpdateUserMetadata(BaseModel):
    role: Optional[Role] = None
    sports: Optional[list[SportType]] = None
    birth_date: Optional[str] = Field(
        None, pattern=BIRTH_DATE_REGEX
    )  # Expected format: 'YYYY/MM/DD'
    user_social_medias: Optional[UserSocialMedias] = None
    profile_description: Optional[str] = Field(None, max_length=500)

    @field_validator("sports")
    def validate_sports(cls, v: Optional[list[SportType]]) -> Optional[list[SportType]]:
        if v and len(v) > 10:
            raise ValueError("A maximum of 10 sports can be specified.")
        return v


class UpdateUserModel(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    username: Optional[str] = Field(None, max_length=50)
    user_metadata: Optional[UpdateUserMetadata] = None


class UpdateUserResponse(BaseModel):
    user: UserModel


class FilterUserResponse(BaseModel):
    num_items: int = Field(..., ge=0)
    users: list[UserModel]
