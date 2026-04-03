---
name: python-web-frameworks
description: "Production Python web development with FastAPI and Django. Invoke when building REST APIs, async endpoints, Pydantic V2 schemas, DRF serializers/viewsets, SQLAlchemy/ORM queries, JWT authentication, Alembic migrations, API versioning, or GraphQL with Strawberry. Covers scaffolding, testing, deployment, and Django-to-FastAPI migration."
triggers:
  - FastAPI endpoint, FastAPI router, FastAPI dependency injection
  - Django view, Django model, DRF serializer, Django ORM
  - Alembic migration, database migration
  - API scaffolding, backend scaffolding
  - JWT auth, OAuth, API authentication
  - Pydantic response model, API schema
  - ASGI, WSGI, uvicorn


<!-- SUMMARY
Scope: FastAPI, Django, DRF, Alembic, API scaffolding, auth patterns
Capabilities: FastAPI with Pydantic V2, Django 5.0, JWT auth, async SQLAlchemy, Alembic migrations
Not for: Python language fundamentals (use python-core), API design theory (use api-design-pro)
END SUMMARY -->

# Python Web Frameworks

Consolidated reference for building production Python APIs with FastAPI, Django/DRF, Alembic, and GraphQL (Strawberry/Ariadne).

## When to Use

- Building REST or GraphQL APIs in Python
- Designing Pydantic V2 schemas or DRF serializers
- Setting up async SQLAlchemy or Django ORM
- Implementing JWT/OAuth2 authentication
- Managing database migrations with Alembic or Django
- Scaffolding new API projects
- Migrating between Django and FastAPI

---

## 1. FastAPI

### Project Structure

```
app/
  api/v1/endpoints/   # Route modules
  core/               # config.py, security.py, database.py
  models/             # SQLAlchemy models
  schemas/            # Pydantic schemas
  services/           # Business logic
  repositories/       # Data access layer
  main.py
```

### Application Bootstrap

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="My API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router, prefix="/api/v1")
```

### Pydantic V2 Schemas

```python
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Self

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    username: str = Field(min_length=3, max_length=50)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Must contain uppercase")
        return v

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)

class UserResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    email: EmailStr
    username: str
    is_active: bool = True

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
```

**V1 to V2 migration cheatsheet:**

| V1 | V2 |
|---|---|
| `@validator` | `@field_validator` |
| `@root_validator` | `@model_validator` |
| `class Config` | `model_config = {}` |
| `orm_mode = True` | `from_attributes = True` |
| `Optional[X]` | `X \| None` |
| `.dict()` | `.model_dump()` |
| `.parse_obj()` | `.model_validate()` |

### Async SQLAlchemy Engine and Session

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, func
from datetime import datetime

engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    posts: Mapped[list["Post"]] = relationship(back_populates="author", lazy="selectin")

async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Router and Dependency Injection

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import Annotated

router = APIRouter(prefix="/users", tags=["users"])
DB = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(db: DB, payload: UserCreate) -> User:
    existing = await crud.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    return await crud.create_user(db, payload)

@router.get("/", response_model=list[UserResponse])
async def list_users(db: DB, current_user: CurrentUser,
                     skip: int = Query(0, ge=0), limit: int = Query(20, le=100)):
    return await crud.get_users(db, skip=skip, limit=limit)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: DB, user_id: int, current_user: CurrentUser) -> None:
    if not await crud.delete_user(db, user_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
```

### JWT Authentication (FastAPI)

```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, UTC

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_access_token(sub: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=15))
    return jwt.encode({"sub": sub, "exp": expire, "type": "access"},
                      settings.SECRET_KEY, algorithm="HS256")

def create_refresh_token(sub: str) -> str:
    expire = datetime.now(UTC) + timedelta(days=7)
    return jwt.encode({"sub": sub, "exp": expire, "type": "refresh"},
                      settings.SECRET_KEY, algorithm="HS256")

async def get_current_user(db: DB, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload["sub"])
        if payload.get("type") != "access":
            raise ValueError
    except (JWTError, ValueError, KeyError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials",
                            headers={"WWW-Authenticate": "Bearer"})
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return user
```

### Role-Based Access

```python
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

def require_roles(*roles: UserRole):
    async def checker(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return current_user
    return checker

AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
```

### Generic CRUD Repository

```python
from typing import Generic, TypeVar, Type
ModelT = TypeVar("ModelT")
CreateT = TypeVar("CreateT", bound=BaseModel)

class BaseRepository(Generic[ModelT, CreateT]):
    def __init__(self, model: Type[ModelT]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> ModelT | None:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: CreateT) -> ModelT:
        obj = self.model(**obj_in.model_dump())
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj
```

### FastAPI Async Testing

```python
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.fixture
async def db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with test_session() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(db):
    app.dependency_overrides[get_db] = lambda: db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
async def auth_headers(test_user):
    token = create_access_token(sub=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    resp = await client.post("/api/v1/users/", json={
        "email": "a@b.com", "username": "alice", "password": "Test1234"
    })
    assert resp.status_code == 201
    assert "password" not in resp.json()
```

---

## 2. Django and DRF

### Model Design with Indexes

```python
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="articles")
    published_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-published_at"]
        indexes = [models.Index(fields=["author", "published_at"])]
```

### ORM Query Optimization

```python
# select_related for FK/OneToOne (single JOIN)
Product.objects.select_related("category", "created_by").all()

# prefetch_related for M2M/reverse FK (separate query)
Product.objects.prefetch_related("tags").all()

# Aggregations
from django.db.models import Count, Avg, F, Q
Category.objects.annotate(product_count=Count("products")).filter(product_count__gt=0)
Product.objects.update(price=F("price") * 1.1)
Product.objects.filter(Q(price__lt=100) | Q(stock__gt=50), is_active=True)

# Partial loading
User.objects.only("id", "email").all()

# Custom manager
class ProductManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)
    def with_related(self):
        return self.select_related("category").prefetch_related("tags")
```

### DRF Serializers

```python
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "price", "category_name", "category_id", "created_at"]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value

    def validate(self, attrs):
        # Cross-field validation
        return attrs
```

### DRF ViewSets

```python
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at"]

    def get_queryset(self):
        return Product.objects.select_related("category", "created_by").all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def purchase(self, request, pk=None):
        product = self.get_object()
        # business logic
        return Response({"status": "ok"})
```

### Django SimpleJWT Authentication

```python
# settings.py
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# Custom claims
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        return token

# Custom permissions
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user
```

### Django 5.0 Async Views

```python
from django.http import JsonResponse
from asgiref.sync import sync_to_async

async def user_list(request):
    users = await sync_to_async(list)(User.objects.all()[:100])
    return JsonResponse({"users": [u.to_dict() for u in users]})
```

### Django Testing

```python
from rest_framework.test import APITestCase
from rest_framework import status
import factory
from factory.django import DjangoModelFactory

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "testpass")

class ArticleAPITest(APITestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_create_requires_auth(self):
        resp = self.client.post("/api/articles/", {"title": "Test"})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_authenticated(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post("/api/articles/", {"title": "Hello Django"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
```

---

## 3. Alembic Migrations

### Setup

```bash
pip install alembic
alembic init alembic
```

Configure `alembic/env.py` to use async engine and import your `Base.metadata`:

```python
# alembic/env.py
from app.core.database import Base
target_metadata = Base.metadata

from sqlalchemy.ext.asyncio import async_engine_from_config

async def run_async_migrations():
    connectable = async_engine_from_config(config.get_section(config.config_ini_section),
                                           prefix="sqlalchemy.")
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
```

### Common Commands

```bash
alembic revision --autogenerate -m "add users table"
alembic upgrade head
alembic downgrade -1
alembic history --verbose
alembic current
```

### Migration Patterns

**Safe column addition (zero downtime):**

```python
def upgrade():
    op.add_column("users", sa.Column("phone", sa.String(20), nullable=True))

def downgrade():
    op.drop_column("users", "phone")
```

**Safe index creation (non-blocking):**

```python
from alembic import op

def upgrade():
    op.execute("CREATE INDEX CONCURRENTLY ix_orders_user ON orders(user_id)")

def downgrade():
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_orders_user")
```

Note: `CONCURRENTLY` cannot run inside a transaction. Set `transaction_per_migration = False` or use `op.execute()` outside `with op.batch_alter_table()`.

**Data migration:**

```python
from alembic import op
from sqlalchemy import table, column, String

def upgrade():
    # Schema change
    op.add_column("users", sa.Column("status", sa.String(20)))
    # Data backfill
    users = table("users", column("status", String))
    op.execute(users.update().values(status="active"))
    # Add NOT NULL after backfill
    op.alter_column("users", "status", nullable=False, server_default="active")
```

### Migration Best Practices

- Always generate with `--autogenerate`, then review before applying.
- Keep each migration small and focused on one change.
- Include both `upgrade()` and `downgrade()`.
- Never edit a migration already applied to shared environments.
- Use `CONCURRENTLY` for index operations on large tables.
- Backfill data in the same migration that adds the column.
- Run `alembic check` in CI to detect drift.

---

## 4. API Versioning Strategies

### URL Path Versioning (recommended)

```python
# FastAPI
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")

# Django
urlpatterns = [
    path("api/v1/", include("api.v1.urls")),
    path("api/v2/", include("api.v2.urls")),
]
```

### Header Versioning

```python
# FastAPI dependency
async def get_api_version(accept: str = Header("application/json")) -> int:
    if "version=2" in accept:
        return 2
    return 1
```

### Deprecation Headers

```python
# FastAPI middleware for deprecated versions
@app.middleware("http")
async def deprecation_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/v1"):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "2025-12-31T00:00:00Z"
        response.headers["Link"] = '</api/v2>; rel="successor-version"'
    return response
```

### Breaking vs Non-Breaking Changes

**Non-breaking (no new version):** adding endpoints, adding optional fields, adding enum values.

**Breaking (requires new version):** removing/renaming fields, changing field types, changing required/optional status.

---

## 5. GraphQL with Strawberry

### Setup

```bash
pip install strawberry-graphql[fastapi]
```

### Schema Definition

```python
import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import Optional

@strawberry.type
class UserType:
    id: int
    email: str
    username: str

@strawberry.input
class UserInput:
    email: str
    username: str
    password: str

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, id: int, info: strawberry.types.Info) -> Optional[UserType]:
        db = info.context["db"]
        result = await db.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        return UserType(id=user.id, email=user.email, username=user.username) if user else None

    @strawberry.field
    async def users(self, limit: int = 20) -> list[UserType]:
        # resolver logic
        ...

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, input: UserInput, info: strawberry.types.Info) -> UserType:
        db = info.context["db"]
        user = User(email=input.email, username=input.username,
                    hashed_password=hash_password(input.password))
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UserType(id=user.id, email=user.email, username=user.username)

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

### Mount in FastAPI

```python
from strawberry.fastapi import GraphQLRouter

async def get_context(db=Depends(get_db)):
    return {"db": db}

graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")
```

### Strawberry with Django

```python
# urls.py
from strawberry.django.views import AsyncGraphQLView

urlpatterns = [
    path("graphql/", AsyncGraphQLView.as_view(schema=schema)),
]
```

### Ariadne Alternative (schema-first)

```python
from ariadne import QueryType, make_executable_schema
from ariadne.asgi import GraphQL

type_defs = """
    type Query {
        user(id: ID!): User
    }
    type User {
        id: ID!
        email: String!
        username: String!
    }
"""

query = QueryType()

@query.field("user")
async def resolve_user(_, info, id):
    db = info.context["db"]
    return await crud.get_user(db, int(id))

schema = make_executable_schema(type_defs, query)
app.mount("/graphql", GraphQL(schema))
```

---

## 6. API Design Patterns

### Standard Response Envelope

```json
{
  "data": { "id": 1, "name": "Alice" },
  "meta": { "request_id": "abc-123" }
}
```

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [{ "field": "email", "message": "must be valid email" }]
  },
  "meta": { "request_id": "abc-123" }
}
```

### FastAPI Exception Handlers

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={
        "error": {"code": exc.code, "message": exc.message}
    })
```

### Pagination (Cursor-Based)

```python
import base64, json

@router.get("/items")
async def list_items(db: DB, limit: int = Query(20, le=100),
                     cursor: str | None = None):
    query = select(Item).order_by(Item.id)
    if cursor:
        decoded = json.loads(base64.b64decode(cursor))
        query = query.where(Item.id > decoded["id"])
    result = await db.execute(query.limit(limit + 1))
    items = list(result.scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    next_cursor = (base64.b64encode(json.dumps({"id": items[-1].id}).encode()).decode()
                   if has_more else None)
    return {"data": items, "next_cursor": next_cursor, "has_more": has_more}
```

### HTTP Status Codes Quick Reference

| Code | Use |
|------|-----|
| 200 | GET/PUT/PATCH success |
| 201 | POST created |
| 204 | DELETE no content |
| 400 | Validation error |
| 401 | Authentication required |
| 403 | Permission denied |
| 404 | Not found |
| 409 | Conflict (duplicate) |
| 429 | Rate limited |

---

## 7. Deployment

### Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose (dev)

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/app
    depends_on: [db]
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: app
      POSTGRES_PASSWORD: postgres
    volumes: [pgdata:/var/lib/postgresql/data]
volumes:
  pgdata:
```

### Quality Gates

- [ ] All tests passing (80%+ coverage)
- [ ] Type checking: `mypy --strict`
- [ ] Linting: `ruff check .`
- [ ] OpenAPI docs valid at `/docs`
- [ ] No hardcoded secrets
- [ ] Migrations up to date (`alembic check`)

---

## 8. Django to FastAPI Migration

Use the **Strangler Pattern**: run both frameworks side by side, migrate endpoints incrementally.

| Django/DRF | FastAPI |
|---|---|
| `models.Model` | SQLAlchemy `DeclarativeBase` |
| `ModelSerializer` | Multiple Pydantic schemas (Create/Read/Update) |
| `ViewSet` | `APIRouter` + path operations |
| `select_related` | `selectinload` / `joinedload` |
| `permissions` | `Depends()` dependencies |
| `settings.py` | `pydantic-settings` |
| `pytest-django` | `pytest-asyncio` + `httpx` |

**Migration phases:**
1. Stand up FastAPI reading shared database (read-only)
2. Migrate GET endpoints first
3. Add write endpoints with dual-write
4. Validate data consistency
5. Full cutover, decommission Django

---

## Constraints

### MUST DO
- Type hints everywhere (FastAPI requires them)
- Pydantic V2 syntax (`field_validator`, `model_config`, `from_attributes`)
- `Annotated` pattern for dependency injection
- `async/await` for all I/O in FastAPI
- `select_related`/`prefetch_related` in Django queries
- Database indexes on frequently queried fields
- Proper HTTP status codes on all endpoints
- Environment variables for all secrets
- Tests for every endpoint (80%+ coverage)

### MUST NOT DO
- Use Pydantic V1 syntax (`@validator`, `class Config`, `Optional[X]`)
- Synchronous DB operations in FastAPI async handlers
- Skip Pydantic/serializer validation
- Store passwords in plain text or secrets in code
- Use `DEBUG=True` or `echo=True` in production
- Ignore N+1 query patterns
- Raw SQL without parameterization
