from fastapi import APIRouter

from core.router import manage

routers: [APIRouter] = [
    manage.router,
]

__all__ = ['routers']
