import os
import sys
import json
from pathlib import Path
from typing import Any

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
USE_POSTGRES = TEST_DATABASE_URL is not None and "postgresql" in TEST_DATABASE_URL

if USE_POSTGRES:
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
else:
    os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

import pytest
from sqlalchemy import create_engine, Text, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import TypeDecorator

if not USE_POSTGRES:
    from sqlalchemy.ext.compiler import compiles

    class JSONArray(TypeDecorator):
        impl = Text
        cache_ok = True

        def process_bind_param(self, value: Any, dialect: Any) -> str | None:
            if value is not None:
                return json.dumps(value)
            return None

        def process_result_value(self, value: Any, dialect: Any) -> list | None:
            if value is not None:
                return json.loads(value)
            return None

    @compiles(ARRAY, 'sqlite')
    def compile_array_sqlite(element, compiler, **kw):
        return "TEXT"

    _original_array_bind_processor = ARRAY.bind_processor

    def _sqlite_array_bind_processor(self, dialect):
        if dialect.name == 'sqlite':
            def process(value):
                if value is not None:
                    return json.dumps(value)
                return None
            return process
        return _original_array_bind_processor(self, dialect)

    ARRAY.bind_processor = _sqlite_array_bind_processor

    _original_array_result_processor = ARRAY.result_processor

    def _sqlite_array_result_processor(self, dialect, coltype):
        if dialect.name == 'sqlite':
            def process(value):
                if value is not None:
                    return json.loads(value)
                return None
            return process
        return _original_array_result_processor(self, dialect, coltype)

    ARRAY.result_processor = _sqlite_array_result_processor


from backend.core.database import Base, get_db
from backend.app import app
from backend.features.user.model import User
from backend.features.project.model import Project
from backend.features.architecture_decision.status.model import Status
from backend.features.documentation_template.model import DocumentationTemplate
from backend.features.documentation_template.fields.model import DocumentationTemplateField
from backend.features.architecture_decision.model import ArchitectureDecision
from backend.features.architecture_decision.fields.model import ArchitectureDecisionFieldValue
from backend.features.project.enum import PriorityLevel
from fastapi.testclient import TestClient


if USE_POSTGRES:
    engine = create_engine(TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db_session):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        email="test@example.com",
        passwordHash=pwd_context.hash("password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_user_2(db_session):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        email="test2@example.com",
        passwordHash=pwd_context.hash("password456"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_project(db_session, sample_user):
    project = Project(
        userID=sample_user.userID,
        name="Test Project",
        description="A test project",
        priority=PriorityLevel.MEDIUM,
        position=0,
        icon="📁",
        color="#4A90E2",
        tags=["test", "sample"],
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def sample_status(db_session):
    status = Status(
        name="Draft",
        color="#808080",
        position=0,
    )
    db_session.add(status)
    db_session.commit()
    db_session.refresh(status)
    return status


@pytest.fixture
def sample_status_2(db_session):
    status = Status(
        name="Approved",
        color="#00FF00",
        position=1,
    )
    db_session.add(status)
    db_session.commit()
    db_session.refresh(status)
    return status


@pytest.fixture
def sample_template(db_session):
    template = DocumentationTemplate(
        name="ADR Template",
        description="Architecture Decision Record template",
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


@pytest.fixture
def sample_template_with_fields(db_session, sample_template):
    field1 = DocumentationTemplateField(
        templateID=sample_template.templateID,
        name="Context",
        isRequired=True,
    )
    field2 = DocumentationTemplateField(
        templateID=sample_template.templateID,
        name="Decision",
        isRequired=True,
    )
    field3 = DocumentationTemplateField(
        templateID=sample_template.templateID,
        name="Consequences",
        isRequired=False,
    )
    db_session.add_all([field1, field2, field3])
    db_session.commit()
    db_session.refresh(sample_template)
    return sample_template


@pytest.fixture
def sample_decision(db_session, sample_project, sample_template_with_fields, sample_status, sample_user):
    decision = ArchitectureDecision(
        projectID=sample_project.projectID,
        templateID=sample_template_with_fields.templateID,
        statusID=sample_status.statusID,
        title="Test Decision",
    )
    db_session.add(decision)
    db_session.commit()
    
    for field in sample_template_with_fields.fields:
        if field.isRequired:
            field_value = ArchitectureDecisionFieldValue(
                decisionID=decision.decisionID,
                fieldID=field.fieldID,
                value=f"Value for {field.name}",
            )
            db_session.add(field_value)
    
    db_session.commit()
    db_session.refresh(decision)
    return decision
