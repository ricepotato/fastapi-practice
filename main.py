from datetime import datetime, time, timedelta
from enum import Enum
from typing import Union
from uuid import UUID

from fastapi import Body, Cookie, FastAPI, Path, Query, Header
from pydantic import BaseModel, Field, HttpUrl


class Item(BaseModel):
    name: str
    description: Union[str, None] = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: Union[float, None] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


app = FastAPI()


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class User(BaseModel):
    username: str
    full_name: str | None = None


@app.post("/items")
async def create_item(item: Item):

    """This is an example of a module level function.

    Function parameters should be documented in the ``Args`` section. The name
    of each parameter is required. The type and description of each parameter
    is optional, but should be included if not obvious.

    If \*args or \*\*kwargs are accepted,
    they should be listed as ``*args`` and ``**kwargs``.

    The format for a parameter is::

        name (type): description
            The description may span multiple lines. Following
            lines should be indented. The "(type)" is optional.

            Multiple paragraphs are supported in parameter
            descriptions.

    Args:
        param1 (int): The first parameter.
        param2 (:obj:`str`, optional): The second parameter. Defaults to None.
            Second line of description should be indented.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        bool: True if successful, False otherwise.

        The return type is optional and may be specified at the beginning of
        the ``Returns`` section followed by a colon.

        The ``Returns`` section may span multiple lines and paragraphs.
        Following lines should be indented to match the first line.

        The ``Returns`` section supports any reStructuredText formatting,
        including literal blocks::

            {
                'param1': param1,
                'param2': param2
            }

    Raises:
        AttributeError: The ``Raises`` section is a list of all exceptions
            that are relevant to the interface.
        ValueError: If `param2` is equal to `param1`.

    """
    return item


# @app.put("/items/{item_id}")
# async def put_item(item_id: int, item: Item, q: str | None = None):
#     result = {"item_id": item_id, **item.dict()}
#     if q:
#         result.update({"q": q})
#     return result


@app.get("/")
async def root():
    return {"message": "Hello world"}


@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(title="The ID of the item to get", default=..., gt=0, le=1000),
    q: Union[str, None] = None,
    size: Union[float, None] = Query(ge=-10, lt=10.5, default=None),
    short: bool = False,
):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.get("/shots/{shot_id}")
async def read_user_item(shot_id: str, needy: str):
    item = {"shot_id": shot_id, "needy": needy}
    return item


@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int = Path(title="The ID of the item to get", ge=0, le=1000),
    q: str | None = None,
    item: Item | None = None,
    user: User | None = None,
    importance: int = Body(default=...)
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    if user:
        results.update({"user": user})
    if importance:
        results.update({"importance": importance})
    return results


class Shot(BaseModel):
    name: str
    thumbnail_url: HttpUrl
    image_url: HttpUrl

    class Config:
        schema_extra = {
            "example": {
                "name": "A schema example",
                "thumbnail_url": "https://ricepotato.bitbucket.io/schema/thumbnail",
                "image_url": "https://ricepotato.bitbucket.io/schema/image",
            }
        }


@app.post("/shots")
async def create_shots(
    shot: Shot = Body(
        examples={
            "normal": {
                "summary": "a normal example",
                "description": "a **normal** item works correctly",
                "value": {
                    "name": "A normal example",
                    "thumbnail_url": "https://ricepotato.bitbucket.io/normal/thumbnail",
                    "image_url": "https://ricepotato.bitbucket.io/normal/image",
                },
            },
            "converted": {
                "summary": "a converted example",
                "description": "a **converted** item works correctly",
                "value": {
                    "name": "A converted example",
                    "thumbnail_url": "https://ricepotato.bitbucket.io/converted/thumbnail",
                    "image_url": "https://ricepotato.bitbucket.io/converted/image",
                },
            },
            "invalid": {
                "summary": "a invalid example",
                "description": "a **invalid** item works correctly",
                "value": {
                    "name": "A invalid example",
                    "thumbnail_url": "https://ricepotato.bitbucket.io/invalid/thumbnail",
                    "image_url": "https://ricepotato.bitbucket.io/invalid/image",
                },
            },
        }
    )
):
    return shot


class ShotV2(BaseModel):
    item_id: UUID


@app.put("/shots/{shot_id}")
async def update_shots(
    shot_id: UUID = Path(example="f902674b-0526-4a35-884a-b2eb809bd7ab"),
    start_datetime: datetime | None = Body(default=None),
    end_datetime: datetime | None = Body(default=None),
    repeat_at: time | None = Body(default=None),
    process_after: timedelta | None = Body(default=None),
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "shot_id": shot_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items")
async def read_item_with_params(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item2(
    user_id: int,
    item_id: str,
    q: Union[str, None] = Query(default=None, min_length=3, max_length=50),
    short: bool = False,
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    return weights


@app.get("/header")
async def get_header(
    user_agent: Union[str, None] = Header(default=None),
    api_key: Union[str, None] = Header(default=None),
):
    return {"User-Agent": user_agent, "api-key": api_key}
