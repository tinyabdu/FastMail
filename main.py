from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from schema import SendEmailRequest

templates = Jinja2Templates(directory="templates")



app = FastAPI(title="Production Email Service")

app.include_router(email_router, prefix="/email")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)