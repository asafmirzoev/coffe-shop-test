import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.environment import env
from app.core.worker import get_worker_id


@asynccontextmanager
async def lifespan(application: FastAPI):
    from app.core.container import Container

    worker_id = get_worker_id()

    await Container.initialize()
    await Container.initialize_services()

    # The initialisation of the database will only be performed in one worker
    if worker_id == 1:
        await Container.initialize_database()

    logging.warning(f'WORKER {worker_id} STARTED')

    yield

    await Container.redis_client.close()


app = FastAPI(
    lifespan=lifespan,
    docs_url='/docs' if env.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def register_rest_routes(application: FastAPI):
    from app.api.rest import auth, users

    application.include_router(
        auth.router,
        prefix='/rest',
    )
    application.include_router(
        users.router,
        prefix='/rest',
    )


register_rest_routes(app)
