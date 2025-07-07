from typing import Literal, Union

from pydantic import HttpUrl

from app.schemas.main import BaseSchema


class Link(BaseSchema):
    url: Union[HttpUrl, str]
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]


class Links(BaseSchema):
    # common for almost all scenarios
    create: Union[Link, None] = None
    view: Union[Link, None] = None
    delete: Union[Link, None] = None
    update: Union[Link, None] = None
    # user route specific
    me: Union[Link, None] = None
    logout: Union[Link, None] = None
    refresh_token: Union[Link, None] = None
