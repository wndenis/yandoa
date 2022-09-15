from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SystemItemType(Enum):
    FILE = 'FILE'
    FOLDER = 'FOLDER'


class SystemItem(BaseModel):
    id: str = Field(..., description='Уникальный идентфикатор', example='элемент_1_1')
    url: str | None = Field(
        None, description='Ссылка на файл. Для папок поле равнно null.'
    )
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


class SystemItemImportRequest(BaseModel):
    items: List[SystemItemImport] | None = Field(
        None, description='Импортируемые элементы'
    )
    updateDate: datetime | None = Field(
        None,
        description='Время обновления добавляемых элементов.',
        example='2022-05-28T21:12:01.000Z',
    )


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
