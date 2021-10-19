from typing import List, Optional

from fastapi import FastAPI, APIRouter

from core import router


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
        if self.instance:
            for r in self.routers:
                self.instance.include_router(r)

    def build(self) -> FastAPI:
        self.apply_router()
        return self.instance


app = FastApiFactory(
    routers=router.routers,
).build()
