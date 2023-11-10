from contextlib import asynccontextmanager
from time import sleep

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.controllers import exploit_db_update, nvd_update
from app.router import api_router
from app.services import create_indexes

DESCRIPTION = """
A backend for dependency graph building, atribution of vulnerabilities and reasoning
over it.
"""


<<<<<<< HEAD
app = FastAPI(
    title='Depex',
    description=DESCRIPTION,
    version='0.6.1',
    contact={
        'name': 'Antonio Germán Márquez Trujillo',
        'url': 'https://github.com/GermanMT',
        'email': 'amtrujillo@us.es',
    },
    license_info={
        'name': 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'url': 'https://www.gnu.org/licenses/gpl-3.0.html',
    },
)


@app.on_event("startup")
async def startup_event() -> None:
=======
@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
>>>>>>> develop
    while True:
        try:
            await create_indexes()
            await exploit_db_update()
            await nvd_update()
            scheduler = BackgroundScheduler()
            scheduler.add_job(nvd_update, "interval", seconds=7200)
            scheduler.add_job(exploit_db_update, "interval", seconds=86400)
            scheduler.start()
            break
        except Exception as _:
            sleep(5)
    yield


app = FastAPI(
    title="Depex",
    description=DESCRIPTION,
    version="0.6.0",
    contact={
        "name": "Antonio Germán Márquez Trujillo",
        "url": "https://github.com/GermanMT",
        "email": "amtrujillo@us.es",
    },
    license_info={
        "name": "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "url": "https://www.gnu.org/licenses/gpl-3.0.html",
    },
    lifespan=lifespan,
)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(
    request: Request, exc: HTTPException
) -> Response:
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> Response:
    return await request_validation_exception_handler(request, exc)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
