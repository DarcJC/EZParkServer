from fastapi import APIRouter

from core.router import manage, client

routers: [APIRouter] = [
    manage.router,
    client.router,
]

__all__ = ['routers']
