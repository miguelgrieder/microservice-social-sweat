from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel


class UserInteractActivityInput(BaseModel):
    user_id: str
    activity_id: str
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
    latitude: float
    longitude: float


class Geometry(BaseModel):
    type: str
    coordinates: Coordinates


class Location(BaseModel):
    country: Country
    area: str
    city: str
    smart_location: str
    geometry: Geometry


class Price(BaseModel):
    value: float
    unit: PriceUnit


class Participants(BaseModel):
    participants_user_id: list[Optional[str]] = []
    max: Optional[int] = None


class Reviews(BaseModel):
    number_of_reviews: int
    review_scores_rating: float


class Host(BaseModel):
    host_user_id: str


class DateTimes(BaseModel):
    datetime_created: str
    datetime_deleted: Optional[str] = None
    datetime_start: Optional[str] = None
    datetime_finish: Optional[str] = None


class Activity(BaseModel):
    id: str
    enabled: bool
    name: str
    description: str
    description_private: Optional[str] = None
    activity_type: ActivityType
    sport_type: SportType
    price: Price
    location: Location
    participants: Participants
    reviews: Reviews
    pictures: List[str]
    host: Host
    datetimes: DateTimes


class CreateActivityInput(BaseModel):
    activity: Activity


class UpdateActivityStateInput(BaseModel):
    action: Literal["enable", "disable"]
    user_id: str
    activity_id: str


class CreateActivityResponse(BaseModel):
    id: str


class UpdateActivityStateResponse(BaseModel):
    acknowledged: bool
    modified_count: int
    matched_count: int


class FilterActivityInput(BaseModel):
    activity_id: Optional[str] = None
    enabled: Optional[bool] = True
    activity_name: Optional[str] = None
    participant_user_id: Optional[str] = None
    host_user_id: Optional[str] = None
    activity_type: Optional[ActivityType] = None
    price: Optional[float] = None
    sport_types: Optional[List[SportType]] = None
    datetime_start: Optional[datetime] = None
    datetime_finish: Optional[datetime] = None

    class Config:
        use_enum_values = True


class FilterActivityResponse(BaseModel):
    num_items: int
    activities: list[Activity]
