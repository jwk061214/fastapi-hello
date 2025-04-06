# FastAPI로 만든 간단한 사용자 관리 백엔드 프로젝트

안녕하세요.  
FastAPI를 처음 공부하면서 만들어 본 사용자 관리 프로젝트입니다.  
회원가입, 로그인, JWT 인증 기능까지 직접 구현해보면서 백엔드 구조를 이해하는 데 많은 도움이 되었습니다.

---

## 프로젝트 개요

- Python의 FastAPI를 활용한 백엔드 개발 연습 프로젝트입니다.
- 기본적인 CRUD 기능과 로그인 기능을 구현했고,
- JWT를 사용해서 인증이 필요한 API도 만들어보았습니다.
- 데이터베이스는 SQLite를 사용했고, ORM은 SQLAlchemy를 사용했습니다.

---

## 주요 기능

- 회원가입 (비밀번호 bcrypt 암호화 저장)
- 로그인 (JWT 토큰 발급)
- 내 정보 조회 (`/me` → 로그인한 사용자만 접근 가능)
- 사용자 전체 조회, 수정, 삭제, 일부 수정 (CRUD)

---

## 사용 기술

- FastAPI
- SQLite + SQLAlchemy
- bcrypt (비밀번호 암호화)
- JWT (python-jose)
- Swagger UI (API 테스트용)

---

## API 명세

| Method | URL             | 설명                     | 인증 여부 |
|--------|------------------|--------------------------|-----------|
| POST   | /signup          | 회원가입                 | X         |
| POST   | /login           | 로그인 → JWT 발급        | X         |
| GET    | /me              | 로그인한 사용자 정보 조회 | O         |
| GET    | /users           | 사용자 전체 목록 조회     | X         |
| PUT    | /users/{id}      | 사용자 정보 전체 수정     | X         |
| PATCH  | /users/{id}      | 사용자 정보 일부 수정     | X         |
| DELETE | /users/{id}      | 사용자 삭제              | X         |

---

## 실행 방법

```bash
# 가상환경 실행
source venv/bin/activate

# 서버 실행
uvicorn main:app --reload

# 브라우저에서 API 문서 보기
http://127.0.0.1:8000/docs

