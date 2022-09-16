from datetime import datetime
from typing import Optional, Union
from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from .creation_validators import validate_unique, validate_existing, validate_parents, validate_urls, validate_size
from .schemas import (
    Error,
    SystemItem,
    SystemItemHistoryResponse,
    SystemItemImportRequest, SystemItemType, SystemItemImport
)
from . import crud, schemas
from .database import Cols, get_cols

app = FastAPI(
    description='Вступительное задание в Осеннюю Школу Бэкенд Разработки Яндекса 2022',
    title='Yet Another Disk Open API',
    version='1.0',
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(schemas.Error(
            code=exc.status_code,
            message=exc.detail
        ))
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder(schemas.Error(
            code=400,
            message=str(exc)
        ))
    )


@app.delete(
    '/delete/{id}',
    response_model=None,
    responses={'400': {'model': Error}, '404': {'model': Error}},
)
async def delete_delete_id(id: str, date: datetime = ..., cols: Cols = Depends(get_cols)) -> Union[None, Error]:
    return await crud.delete_file_recursively(id, cols)


@app.post('/imports', response_model=None, responses={'400': {'model': Error}})
async def post_imports(body: SystemItemImportRequest = None, cols: Cols = Depends(get_cols)) -> Union[None, Error]:
    validate_unique(body)
    await validate_existing(body, cols)
    await validate_parents(body, cols)
    validate_urls(body)
    validate_size(body)
    elements = [elem.to_system_item(body.updateDate) for elem in body.items]

    folders = [elem for elem in elements if elem.type == SystemItemType.FOLDER]
    files = [elem for elem in elements if elem.type == SystemItemType.FILE]
    entries = folders
    entries.extend(files)
    for elem in entries:
        if elem.size is None:
            elem.size = 0
        if await crud.check_file_exists(elem.id, cols):
            await crud.update_file(elem, cols)
        else:
            await crud.create_file(elem, cols)


@app.get(
    '/node/{id}/history',
    response_model=SystemItemHistoryResponse,
    responses={'400': {'model': Error}, '404': {'model': Error}},
)
async def get_node_id_history(
        id: str,
        date_start: Optional[datetime] = Query(None, alias='dateStart'),
        date_end: Optional[datetime] = Query(None, alias='dateEnd'),
        cols=Depends(get_cols)
) -> Union[SystemItemHistoryResponse, Error]:
    return await crud.get_history(id, date_start, date_end, cols)


@app.get('/nodes/{id}', response_model=SystemItem, responses={'404': {'model': Error}})
async def get_nodes_id(id: str, cols: Cols = Depends(get_cols)) -> Union[SystemItem, Error]:
    result = await crud.find_file(id, cols)
    if result:
        return result
    raise HTTPException(status_code=404, detail="File not found")


@app.get(
    '/updates',
    response_model=SystemItemHistoryResponse,
    responses={'400': {'model': Error}},
)
async def get_updates(date: datetime, cols: Cols = Depends(get_cols)) -> Union[SystemItemHistoryResponse, Error]:
    results = await crud.get_updates(date, cols)
    return SystemItemHistoryResponse(items=results)
