import re
from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator

USER_ID_REGEX = r".*"
ACTIVITY_ID_REGEX = r".*"


class UserInteractActivityInput(BaseModel):
    user_id: str = Field(..., pattern=USER_ID_REGEX)
    activity_id: str = Field(..., pattern=ACTIVITY_ID_REGEX)
    action: Literal["join", "leave"]


class SportType(str, Enum):
    gym = "gym"
    basketball = "basketball"
    soccer = "soccer"
    tennis = "tennis"
    yoga = "yoga"
    triathlon = "triathlon"
    run = "run"
    martial_arts = "martial_arts"  # karate
    motorsports = "motorsports"  # racing-helmet
    volleyball = "volleyball"
    handball = "handball"
    hockey = "hockey"
    ski = "ski"
    ski_water = "ski_water"
    baseball = "baseball"
    skateboard = "skateboard"  # skateboarding
    esports = "esports"  # gamepad-variant-outline
    swim = "swim"
    other = "other"  # water-outline


class ActivityType(str, Enum):
    spot = "spot"
    event = "event"
    session = "session"


class PriceUnit(str, Enum):
    dollar = "$"
    real = "R$"
    euro = "€"


class Country(str, Enum):
    brazil = "Brazil"
    united_states = "United States"
    germany = "Germany"


class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class Geometry(BaseModel):
    type: Literal["Point"]
    coordinates: Coordinates


class Location(BaseModel):
    country: Country
    area: str = Field(..., max_length=100)
    city: str = Field(..., max_length=100, min_length=2)
    smart_location: str = Field(..., max_length=200, min_length=2)
    geometry: Geometry


class Price(BaseModel):
    value: float = Field(..., ge=0)
    unit: PriceUnit


class Participants(BaseModel):
    participants_user_id: list[Optional[str]] = Field(default_factory=list)
    max: Optional[int] = Field(None, gt=0)

    @field_validator("participants_user_id", mode="after")
    def validate_participant_user_id(cls, v: list[str]) -> list[str]:
        for user_id in v:
            if not re.match(USER_ID_REGEX, user_id):
                raise ValueError("Invalid participant user ID format.")
        return v

    @model_validator(mode="after")  # type: ignore[arg-type]
    @classmethod
    def validate_participants_count(
        cls, values: "Participants", info: ValidationInfo
    ) -> "Participants":
        participants_user_id = values.participants_user_id
        max_participants = values.max
        if max_participants is not None and len(participants_user_id) > max_participants:
            raise ValueError("Number of participants exceeds the maximum allowed.")
        return values


class Host(BaseModel):
    host_user_id: str = Field(..., pattern=USER_ID_REGEX)


class DateTimes(BaseModel):
    datetime_created: str
    datetime_deleted: Optional[str] = None
    datetime_start: Optional[str] = None
    datetime_finish: Optional[str] = None

    # @model_validator(mode="after")  # type: ignore[arg-type]
    # @classmethod
    # def validate_datetime_order(cls, values: "DateTimes", info: ValidationInfo) -> "DateTimes":
    #     datetime_start = values.datetime_start
    #     datetime_finish = values.datetime_finish
    #     if datetime_start and datetime_finish and datetime_finish < datetime_start:
    #         raise ValueError("datetime_finish must be after datetime_start.")
    #     return values


class Activity(BaseModel):
    id: str
    enabled: bool
    name: str = Field(..., max_length=100, min_length=5)
    description: str = Field(..., max_length=1000, min_length=10)
    description_private: Optional[str] = Field(None, max_length=1000)
    activity_type: ActivityType
    sport_type: SportType
    price: Price
    location: Location
    participants: Participants
    pictures: list[str]
    host: Host
    datetimes: DateTimes

    @field_validator("pictures", mode="after")
    def validate_pictures_count(cls, v: list[str]) -> list[str]:
        if len(v) > 10:
            raise ValueError("Too many pictures; maximum allowed is 10.")
        return v


class CreateActivityInput(BaseModel):
    activity: Activity


class UpdateActivityStateInput(BaseModel):
    action: Literal["enable", "disable"]
    user_id: str = Field(..., pattern=USER_ID_REGEX)
    activity_id: str = Field(..., pattern=ACTIVITY_ID_REGEX)


class CreateActivityResponse(BaseModel):
    id: str = Field(..., pattern=ACTIVITY_ID_REGEX)


class UpdateActivityStateResponse(BaseModel):
    acknowledged: bool
    modified_count: int
    matched_count: int


class FilterActivityInput(BaseModel):
    activity_id: Optional[str] = Field(None, pattern=ACTIVITY_ID_REGEX)
    enabled: Optional[bool] = True
    activity_name: Optional[str] = Field(None, max_length=100)
    participant_user_id: Optional[str] = Field(None, pattern=USER_ID_REGEX)
    host_user_id: Optional[str] = Field(None, pattern=USER_ID_REGEX)
    activity_type: Optional[ActivityType] = None
    price: Optional[float] = Field(None, ge=0)
    sport_types: Optional[list[SportType]] = None
    datetime_start: Optional[datetime] = None
    datetime_finish: Optional[datetime] = None

    class Config:
        use_enum_values = True

    # @model_validator(mode="after")  # type: ignore[arg-type]
    # @classmethod
    # def validate_datetime_range(
    #     cls, values: "FilterActivityInput", info: ValidationInfo
    # ) -> "FilterActivityInput":
    #     datetime_start = values.datetime_start
    #     datetime_finish = values.datetime_finish
    #     if datetime_start and datetime_finish and datetime_finish < datetime_start:
    #         raise ValueError("datetime_finish must be after datetime_start.")
    #     return values


class FilterActivityResponse(BaseModel):
    num_items: int
    activities: list[Activity]
