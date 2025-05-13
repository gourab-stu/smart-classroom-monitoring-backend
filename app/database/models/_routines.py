from datetime import datetime
from typing import Literal
from beanie import Document, Link
from pydantic import Field
from pymongo import IndexModel

from app.database.models._papers import Paper
from app.database.models._teachers import Teacher


class Routine(Document):
    day: Literal[
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ] = Field(
        default=...,
        description="Name of the day of the class"
    )
    semester: Literal[1, 2, 3, 4, 5, 6, 7, 8] = Field(
        default=...,
        description="Which semester's class it is"
    )
    teacher: Link[Teacher] = Field(
        default=...,
        description="ObjectId of the teacher who will be taking the class"
    )
    paper: Link[Paper] = Field(
        default=...,
        description="ObjectId of the paper that will be discussed"
    )
    starting_time: datetime = Field(
        default=...,
        description="Starting time of the class"
    )
    ending_time: datetime = Field(
        default=...,
        description="Ending time of the class"
    )

    class Settings:
        name: str = "routines"
        # indexes: list[IndexModel] = [
        #     IndexModel(keys=[()])
        # ]
