from fastapi import FastAPI, File

from reports import router


app = FastAPI()
app.include_router(router)
