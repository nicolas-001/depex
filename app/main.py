from json import loads
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from app.controllers import db_updater
from app.router import api_router
from app.services import create_indexes
from app.utils import json_encoder

DESCRIPTION = '''
A backend for dependency graph building, atribution of vulnerabilities and reasoning
over it.
'''

app = FastAPI(
    title='Depex',
    description=DESCRIPTION,
    version='0.5.0',
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
    await create_indexes()
    await db_updater()
    scheduler = BackgroundScheduler()
    scheduler.add_job(db_updater, 'interval', seconds=216000)
    scheduler.start()


@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(_: Request, exc: ValidationError | RequestValidationError) -> JSONResponse:
    exc_json = loads(exc.json())
    response: dict[str, list[str]] = {'message': []}
    for error in exc_json:
        response['message'].append(error['loc'][-1] + f": {error['msg']}")

    return JSONResponse(content=json_encoder(response), status_code=422)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(api_router)