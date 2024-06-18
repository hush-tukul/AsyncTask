from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from config import async_session, init_db
from models import UserData

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    # No explicit cleanup needed unless you have resources that require manual teardown


app.lifespan = lifespan


# Dependency to get the session
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@app.get("/", response_class=HTMLResponse)
async def serve_index(session: AsyncSession = Depends(get_session)):
    try:
        users = await get_users(session)
        with open("templates/index.html", "r") as file:
            content = file.read()
        users_html = "".join(f"<li>{user.name} ({user.email})</li>" for user in users)
        return HTMLResponse(
            content.replace("<!-- Users will be displayed here -->", users_html)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/get_users", response_class=JSONResponse)
async def get_users_json(session: AsyncSession = Depends(get_session)):
    try:
        users = await get_users(session)
        return [{"name": user.name, "email": user.email} for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def get_users(session: AsyncSession):
    statement = select(UserData)
    result = await session.execute(statement)
    return result.scalars().all()


@app.post("/api/submit")
async def submit(name: str = Form(...), email: str = Form(...)):
    try:
        new_user_data = UserData(name=name, email=email)
        async with async_session() as session:
            session.add(new_user_data)
            await session.commit()
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
