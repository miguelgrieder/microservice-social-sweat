from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from microservice_social_sweat.services.activities.models import SportType


class UserSocialMedias(BaseModel):
    user_youtube: Optional[str] = None
    user_instagram: Optional[str] = None
    user_facebook: Optional[str] = None
    user_tiktok: Optional[str] = None
    user_strava: Optional[str] = None
    user_phone: Optional[str] = None
    use_phone: Optional[bool] = None
    use_sms: Optional[bool] = None
    use_whatsapp: Optional[bool] = None

class UserMetrics(BaseModel):
    activities_created: int = 0
    activities_participated: int = 0
    activities_participating: int = 0


class FilterUserInput(BaseModel):
    role: Optional[str] = None
    id: Optional[str] = None
    username: Optional[str] = None
    sport_type: Optional[SportType] = None


class Role(str, Enum):
    coach = "coach"
    user = "user"
    company = "company"


class UserMetadata(BaseModel):
    role: Role
    sports: list[Optional[SportType]] = []
    birth_date: str
    user_social_medias: UserSocialMedias = UserSocialMedias()
    profile_description: Optional[str] = None
    user_metrics: UserMetrics = UserMetrics()


class UserModel(BaseModel):
    id: str
    user_metadata: UserMetadata
    email_address: Optional[str]
    phone_number: Optional[str]
    image_url: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    last_active_at: Optional[int]
    created_at: int

    @staticmethod
    def from_clerk_user_request(user: dict[str, Any]) -> "UserModel":
        unsafe_metadata = user.get("unsafe_metadata", {})

        role = unsafe_metadata.get("role")
        sports = unsafe_metadata.get("sports", [])
        birth_date = unsafe_metadata.get("birth_date")
        profile_description = unsafe_metadata.get("profile_description")

        user_social_medias = UserSocialMedias(**unsafe_metadata.get("user_social_medias", {}))

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
    sports: Optional[list[Optional[SportType]]] = None
    birth_date: Optional[str] = None  # Expected format: 'YYYY/MM/DD'
    user_social_medias: Optional[UserSocialMedias] = None
    profile_description: Optional[str] = None


class UpdateUserModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    user_metadata: Optional[UpdateUserMetadata] = None


class UpdateUserResponse(BaseModel):
    user: UserModel


class FilterUserResponse(BaseModel):
    num_items: int
    users: list[UserModel]
