from datetime import datetime
from typing import Optional, Union

from fastapi import FastAPI, Query

from .models import (
    Error,
    SystemItem,
    SystemItemHistoryResponse,
    SystemItemImportRequest
)

app = FastAPI(
    description='Вступительное задание в Осеннюю Школу Бэкенд Разработки Яндекса 2022',
    title='Yet Another Disk Open API',
    version='1.0',
)


@app.delete(
    '/delete/{id}',
    response_model=None,
    responses={'400': {'model': Error}, '404': {'model': Error}},
)
def delete_delete_id(id: str, date: datetime = ...) -> Union[None, Error]:
    pass


@app.post('/imports', response_model=None, responses={'400': {'model': Error}})
def post_imports(body: SystemItemImportRequest = None) -> Union[None, Error]:
    pass


@app.get(
    '/node/{id}/history',
    response_model=SystemItemHistoryResponse,
    responses={'400': {'model': Error}, '404': {'model': Error}},
)
def get_node_id_history(
        id: str,
        date_start: Optional[datetime] = Query(None, alias='dateStart'),
        date_end: Optional[datetime] = Query(None, alias='dateEnd'),
) -> Union[SystemItemHistoryResponse, Error]:
    pass


@app.get('/nodes/{id}', response_model=SystemItem, responses={'404': {'model': Error}})
def get_nodes_id(id: str) -> Union[SystemItem, Error]:
    pass


@app.get(
    '/updates',
    response_model=SystemItemHistoryResponse,
    responses={'400': {'model': Error}},
)
def get_updates(date: datetime) -> Union[SystemItemHistoryResponse, Error]:
    pass
