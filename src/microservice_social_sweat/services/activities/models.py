from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, condecimal


class Filter(BaseModel):
    activity_id: Optional[int]


class SportType(str, Enum):
    gym = "gym"
    basketball = "basketball"
    soccer = "soccer"
    tennis = "tennis"
    # Temporary
    weight_lifter = "weight-lifter"
    yoga = "yoga"
    run_fast = "run-fast"


class ActivityType(str, Enum):
    public_spot = "Public Spot"
    private_spot = "Private Spot"
    event = "Event"
    session = "Session"


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
    current: int
    max: Optional[int] = None


class Reviews(BaseModel):
    number_of_reviews: int
    review_scores_rating: float


class Host(BaseModel):
    host_picture_url: HttpUrl
    host_name: str
    host_since: str


class DateTimes(BaseModel):
    datetime_created: str
    datetime_deleted: Optional[str] = None
    datetime_start: str
    datetime_finish: str


class Activity(BaseModel):
    id: int
    name: str
    description: str
    activity_type: ActivityType
    sport_type: SportType
    price: Price
    location: Location
    participants: Participants
    reviews: Reviews
    pictures: List[HttpUrl]
    host: Host
    datetimes: DateTimes
