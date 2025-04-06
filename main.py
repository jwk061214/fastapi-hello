from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

from typing import List
from models import User

from typing import Optional
from pydantic import BaseModel

import bcrypt

from auth import create_access_token
from pydantic import BaseModel
import bcrypt
from datetime import timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from auth import get_current_user
from auth import SECRET_KEY, ALGORITHM


# 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class SignUpRequest(BaseModel):
    name: str
    age: int
    email: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserRequest(BaseModel):
    name: str
    age: int

@app.post("/users")
def create_user(request: UserRequest, db: Session = Depends(get_db)):
    user = models.User(name=request.name, age=request.age)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": f"{user.name}님({user.age}살) 저장 완료!"}



@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []
    for user in users:
        result.append({"id":user.id,"name":user.name,"age":user.age})
    return result

@app.get("/users/adults")
def get_adults(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.age<20).all()
    adult_list = []
    for user in users:
        adult_list.append({"id":user.id,"name":user.name,"age":user.age}) 
    return adult_list


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    db.delete(user)
    db.commit()
    return {"message": f"{user.name}님이 삭제되었습니다."}

class UpdateUserRequest(BaseModel):
    name: str
    age: int

@app.put("/users/{user_id}")
def update_user(user_id: int, request: UpdateUserRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    user.name = request.name
    user.age = request.age
    db.commit()
    db.refresh(user)

    return {"message": f"{user.id}번 사용자 정보가 수정되었습니다.", "data": {
        "id": user.id,
        "name": user.name,
        "age": user.age
    }}
class PatchUserRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None

@app.patch("/users/{user_id}")
def patch_user(user_id: int, request: PatchUserRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    mas = []
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    if request.name is not None:
        user.name = request.name
        mas.append('이름이 변경됨.')
    if request.age is not None:
        user.age = request.age
        mas.append('이름이 변경됨.')


    db.commit()
    db.refresh(user)

    
    return {
        "message": f"{user.id}번 사용자 정보가 부분 수정되었습니다.".join(mas),
        "data": {"id": user.id, "name": user.name, "age": user.age}
    }
@app.post("/signup")
def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    # 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    # 비밀번호 암호화
    hashed_pw = bcrypt.hashpw(request.password.encode("utf-8"), bcrypt.gensalt())

    # 사용자 저장
    user = User(
        name=request.name,
        age=request.age,
        email=request.email,
        password=hashed_pw.decode("utf-8")
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": f"{user.name}님, 회원가입이 완료되었습니다."}




class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="존재하지 않는 사용자입니다.")

    if not bcrypt.checkpw(request.password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")

    # JWT 토큰 발급
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=30)
    )

    return {"access_token": access_token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="로그인이 필요합니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception

def read_current_user(email: str = Depends(get_current_user)):
    return {"message": f"{email}님, 환영합니다!"}
