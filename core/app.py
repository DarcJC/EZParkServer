from typing import List, Optional

from fastapi import FastAPI, APIRouter
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from core import router, settings
from core.dependencies import InvalidTokenError


class FastApiFactory(object):
    def __init__(
            self,
            routers: Optional[List[APIRouter]] = None,
    ):
        self.instance = FastAPI(
            title="EZPark",
            description="停车系统后端程序接口",
            version="1.0.0",
        )
        self.routers = routers

    def apply_router(self):
        if self.instance and self.routers:
            for r in self.routers:
                self.instance.include_router(r)

    def apply_tortoise_middleware(self):
        if self.instance:
            register_tortoise(
                self.instance,
                db_url=settings.DATABASE_URI,
                modules={"models": ["core.models", ]},
                generate_schemas=False,
                add_exception_handlers=True,
            )

    def build(self) -> FastAPI:
        self.apply_router()
        self.apply_tortoise_middleware()
        return self.instance


app = FastApiFactory(
    routers=router.routers,
).build()


@app.on_event("shutdown")
async def shutdown():
    from tortoise import Tortoise
    await Tortoise.close_connections()


@app.exception_handler(InvalidTokenError)
def invalid_token_error(_: Request, __: InvalidTokenError):
    return JSONResponse({
        "detail": "Bad admin token",
    }, 400)
