from fastapi import HTTPException

from app import crud
from app.database import Cols
from app.schemas import SystemItemImportRequest, SystemItemType


def assert_http(value, message):
    if value:
        return
    raise HTTPException(status_code=400, detail=message)


def validate_unique(body: SystemItemImportRequest):
    unique = set([elem.id for elem in body.items])
    assert_http(len(unique) == len(body.items), "No duplicate ids allowed")


async def validate_existing(body: SystemItemImportRequest, cols: Cols):
    for item in body.items:
        exists = await crud.find_file(item.id, cols, True)
        if exists:
            assert_http(item.type == exists.type, "No type change allowed")


async def validate_parents(body: SystemItemImportRequest, cols: Cols):
    new_ids = {elem.id for elem in body.items}
    target_parents = [elem.parentId for elem in body.items]
    for target_parent in target_parents:
        if target_parent is None:
            continue
        if target_parent in new_ids:
            continue
        if await crud.check_file_exists(target_parent, cols):
            continue
        raise HTTPException(status_code=400, detail="Impossible parents")


def validate_urls(body: SystemItemImportRequest):
    for elem in body.items:
        if elem.type == SystemItemType.FOLDER:
            assert_http(elem.url is None, "Folder can not have url")
        elif elem.type == SystemItemType.FILE:
            assert_http(elem.url is not None, "File must have url")
        if elem.url is not None:
            assert_http(len(elem.url) <= 255, "Url must be 255 chars or less")


def validate_size(body: SystemItemImportRequest):
    for elem in body.items:
        if elem.type == SystemItemType.FILE:
            assert_http(elem.size is not None, "File must have non-negative size")
            assert_http(elem.size >= 0, "File must have non-negative size")
        elif elem.type == SystemItemType.FOLDER:
            assert_http(elem.size is None or elem.size == 0, "You can not set folder size explicitly")
