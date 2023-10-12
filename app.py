from fastapi import FastAPI

from reports import router

app = FastAPI()
app.include_router(router)
