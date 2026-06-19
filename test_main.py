from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db, Base
from models import TaskDB

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# ── GET /tasks ────────────────────────────────────────────────
def test_get_all_tasks_returns_200():
    response = client.get("/tasks")
    assert response.status_code == 200

def test_get_all_tasks_returns_empty_list_initially():
    response = client.get("/tasks")
    assert response.json() == []


# ── POST /tasks ───────────────────────────────────────────────
def test_create_task_returns_201():
    response = client.post("/tasks", json={"title": "Test task", "status": "pending"})
    assert response.status_code == 201

def test_create_task_default_priority_is_medium():
    response = client.post("/tasks", json={"title": "No priority set"})
    assert response.json()["priority"] == "medium"

def test_create_task_with_priority_and_due_date():
    response = client.post("/tasks", json={
        "title": "Important task",
        "priority": "high",
        "due_date": "2026-06-20"
    })
    task = response.json()
    assert task["priority"] == "high"
    assert task["due_date"] == "2026-06-20"

def test_create_task_done_sets_completed_at():
    response = client.post("/tasks", json={"title": "Already done", "status": "done"})
    assert response.json()["completed_at"] is not None

def test_create_task_pending_has_no_completed_at():
    response = client.post("/tasks", json={"title": "Still pending", "status": "pending"})
    assert response.json()["completed_at"] is None


# ── PUT /tasks/{task_id} ──────────────────────────────────────
def test_marking_task_done_sets_completed_at():
    created = client.post("/tasks", json={"title": "Mark me done", "status": "pending"}).json()
    response = client.put(f"/tasks/{created['id']}", json={"title": "Mark me done", "status": "done"})
    assert response.json()["completed_at"] is not None

def test_unmarking_done_clears_completed_at():
    created = client.post("/tasks", json={"title": "Undo me", "status": "done"}).json()
    assert created["completed_at"] is not None
    response = client.put(f"/tasks/{created['id']}", json={"title": "Undo me", "status": "pending"})
    assert response.json()["completed_at"] is None

def test_update_task_changes_priority():
    created = client.post("/tasks", json={"title": "Priority test", "priority": "low"}).json()
    response = client.put(f"/tasks/{created['id']}", json={"title": "Priority test", "priority": "high", "status": "pending"})
    assert response.json()["priority"] == "high"


# ── GET /tasks/{task_id} ──────────────────────────────────────
def test_get_task_not_found_returns_404():
    response = client.get("/tasks/9999")
    assert response.status_code == 404

def test_get_task_invalid_id_returns_422():
    response = client.get("/tasks/abc")
    assert response.status_code == 422


# ── DELETE /tasks/{task_id} ───────────────────────────────────
def test_delete_task_returns_200():
    created = client.post("/tasks", json={"title": "Delete me"}).json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 200

def test_delete_task_not_found_returns_404():
    response = client.delete("/tasks/9999")
    assert response.status_code == 404