#!/usr/bin/env python
import signal
from typing import Optional

import typer
from tortoise import Tortoise, run_async

app = typer.Typer()


@app.command("dev", help="启动本地开发服务器")
def dev(
        *,
        host: Optional[str] = "127.0.0.1",
        port: Optional[int] = 5000,
        reload: Optional[bool] = True,
):
    import uvicorn
    uvicorn.run("core:app", host=host, port=port, log_level="info", reload=reload, workers=1)


@app.command("setup", help="初始化运行环境, 初次运行前调用")
def setup():
    async def task():
        await Tortoise.init(
            db_url="",
            modules={
                "models": ["core.models"],
            },
        )
        await Tortoise.generate_schemas()

    run_async(task())


signal.signal(signal.SIGTERM, lambda: (_ for _ in ()).throw(typer.Abort))

if __name__ == '__main__':
    app()
