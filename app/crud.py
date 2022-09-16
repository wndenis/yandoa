from datetime import datetime, timedelta

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from . import schemas
from .database import Cols
from .schemas import SystemItemType


async def check_file_exists(id: str, cols: Cols):
    file_exists = await cols.files_collection.find_one({"id": id})
    if file_exists:
        return True
    return False


async def find_children_id(id: str, cols: Cols):
    cur = cols.files_collection.find({"parentId": id})
    result = await cur.to_list(length=10000)
    if result:
        result = [elem["id"] for elem in result]
    return result


async def update_file(file: schemas.SystemItem, cols: Cols):
    existing = await find_file(file.id, cols, True)
    old_parent = existing.parentId
    if file.parentId != old_parent:
        await update_parent_size(file.id, cols, None, minus)  # remove space in prev pos
    dic = jsonable_encoder(file)
    del dic["children"]
    await cols.files_collection.update_one({"id": file.id}, {"$set": dic})
    await record_history(file.id, cols)
    await update_parent_size(file.id, cols, None, plus)  # add space in new pos


async def create_file(file: schemas.SystemItemImport, cols: Cols):
    try:
        file = jsonable_encoder(file)
    except:
        pass
    await cols.files_collection.insert_one(file)
    await update_parent_size(file["id"], cols, None, plus)
    await record_history(file["id"], cols)


async def find_file(id: str, cols: Cols, flat=False) -> schemas.SystemItem:
    cur = cols.files_collection.find({"id": id})
    doc = await cur.to_list(length=1)
    if not doc:
        return
    doc = doc[0]
    if flat:
        return schemas.SystemItem(**doc)

    if doc["type"] == SystemItemType.FILE.value:
        doc["children"] = None
    elif doc["type"] == SystemItemType.FOLDER.value:
        children_list = await find_children_id(id, cols)
        doc["children"] = [await find_file(elem, cols) for elem in children_list]
    return schemas.SystemItem(**doc)


async def update_parent_size(current_id: str, cols: Cols, delta: int | None, formula: callable):
    file = await find_file(current_id, cols, True)
    if delta is None:
        delta = file.size
    if file.parentId is not None:
        parent = await find_file(file.parentId, cols, True)
        if file.date > parent.date:
            parent.date = file.date
            await cols.files_collection.replace_one({"id": file.parentId}, jsonable_encoder(parent))
        old_size = (await find_file(file.parentId, cols, flat=True)).size
        new_size = formula(old_size, delta)
        await cols.files_collection.update_one({"id": file.parentId}, {"$set": {"size": new_size}})
        await update_parent_size(file.parentId, cols, delta, formula)
        await record_history(file.parentId, cols)


def minus(a, b):
    return a - b


def plus(a, b):
    return a + b


async def record_history(id: str, cols: Cols):
    file = await find_file(id, cols, True)
    search = await cols.history_collection.find_one({"id": file.id})
    if search:
        await cols.history_collection.update_one({"id": file.id},
                                                 {"$push": {"history": jsonable_encoder(file)}})
    else:
        await cols.history_collection.insert_one({
            "id": file.id,
            "history": [jsonable_encoder(file)]
        })


async def delete_file_recursively(id: str, cols: Cols):
    file_exists = await check_file_exists(id, cols)
    if not file_exists:
        raise HTTPException(status_code=404, detail="Item to delete not found")
    await update_parent_size(id, cols, None, minus)
    children_id = await find_children_id(id, cols)
    for child_id in children_id:
        await delete_file(child_id, cols)
    await delete_file(id, cols)


async def delete_file(id: str, cols: Cols):
    await cols.files_collection.delete_one({"id": id})
    await cols.history_collection.delete_one({"id": id})


async def get_updates(date: datetime, cols: Cols):
    cur = cols.files_collection.find({"date": {"$lte": date, "$gte": date - timedelta(hours=24)}})
    doc = await cur.to_list(length=1000)
    return doc


async def get_history(id: str, date_start: datetime, date_end: datetime, cols: Cols):
    cur = cols.history_collection.find({"id": id, "history.date": {"$lt": date_end, "$gte": date_start}})
    doc = await cur.to_list(length=1000)
    return doc
