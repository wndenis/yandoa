from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel as BM, Field, validator

# import dateutil

# ====== schemas
# from app.utils import parse_time_str

DATE_PATTERN = '%Y-%m-%dT%H:%M:%SZ'


class BaseModel(BM):
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime(DATE_PATTERN)
        }


class SystemItemType(Enum):
    FILE = 'FILE'
    FOLDER = 'FOLDER'


class SystemItem(BaseModel):
    id: str = Field(..., description='Уникальный идентфикатор', example='элемент_1_1')
    url: str | None = Field(
        None, description='Ссылка на файл. Для папок поле равнно null.'
    )
    # @validator("url")
    # def len_limit(cls, v):
    #
    #     return v

    date: datetime = Field(
        ...,
        description='Время последнего обновления элемента.',
        example='2022-05-28T21:12:01.000Z',
    )
    parentId: str | None = Field(
        None, description='id родительской папки', example='элемент_1_1'
    )
    type: SystemItemType
    size: int | None = Field(
        None, description='Целое число, для папки - это суммарный размер всех элеметов.'
    )
    children: List["SystemItem"] | None = Field(
        None, description='Список всех дочерних элементов. Для файлов поле равно null.'
    )


class SystemItemImport(BaseModel):
    id: str = Field(..., description='Уникальный идентфикатор', example='элемент_1_1')
    url: str | None = Field(
        None, description='Ссылка на файл. Для папок поле равнно null.'
    )
    parentId: str | None = Field(
        None, description='id родительской папки', example='элемент_1_1'
    )
    type: SystemItemType
    size: int | None = Field(
        None, description='Целое число, для папок поле должно содержать null.'
    )

    def to_system_item(self, timestamp):
        self_repr = self.dict()
        self_repr["date"] = timestamp
        result = SystemItem(**self_repr)
        return result


class SystemItemImportRequest(BaseModel):
    items: List[SystemItemImport] | None = Field(
        None, description='Импортируемые элементы'
    )
    updateDate: datetime | None = Field(
        None,
        description='Время обновления добавляемых элементов.',
        example='2022-05-28T21:12:01.000Z',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SystemItemHistoryUnit(BaseModel):
    id: str = Field(..., description='Уникальный идентфикатор', example='элемент_1_1')
    url: str | None = Field(
        None, description='Ссылка на файл. Для папок поле равнно null.'
    )
    parentId: str | None = Field(
        None, description='id родительской папки', example='элемент_1_1'
    )
    type: SystemItemType
    size: int | None = Field(
        None,
        description='Целое число, для папки - это суммарный размер всех её элементов.',
    )
    date: datetime = Field(..., description='Время последнего обновления элемента.')


class SystemItemHistoryResponse(BaseModel):
    items: List[SystemItemHistoryUnit] | None = Field(
        None, description='История в произвольном порядке.'
    )


class Error(BaseModel):
    code: int
    message: str
