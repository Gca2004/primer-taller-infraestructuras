from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, Base
from prometheus_client import Counter, Gauge, generate_latest
from fastapi.responses import Response

app = FastAPI()
USER_CREATED = Counter("user_created", "Number of users created")
TOTAL_USERS = Gauge("total_users", "Total users in database")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    TOTAL_USERS.set(len(users))
    return users

@app.post("/users")
def create_user(name: str, age: int, db: Session = Depends(get_db)):
    user = User(name=name, age=age)
    db.add(user)
    db.commit()
    db.refresh(user)
    USER_CREATED.inc()
    TOTAL_USERS.inc()
    return user

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")