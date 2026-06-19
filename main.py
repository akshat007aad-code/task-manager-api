from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import TaskDB, TaskCreate, TaskResponse
from database import engine, get_db, Base
from typing import List
from datetime import datetime, timezone
 
Base.metadata.create_all(bind=engine)
 
app = FastAPI()
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
@app.get("/tasks", response_model=List[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(TaskDB).all()
 
 
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
 
 
@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = TaskDB(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
    )
    if task.status == "done":
        new_task.completed_at = datetime.now(timezone.utc).isoformat()
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
 
 
@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, updated: TaskCreate, db: Session = Depends(get_db)):
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    was_done = task.status == "done"
    now_done = updated.status == "done"
    task.title = updated.title
    task.description = updated.description
    task.status = updated.status
    task.priority = updated.priority
    task.due_date = updated.due_date
    if now_done and not was_done:
        task.completed_at = datetime.now(timezone.utc).isoformat()
    elif not now_done:
        task.completed_at = None
    db.commit()
    db.refresh(task)
    return task
 
 
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": f"Task {task_id} deleted successfully"}
 
 
# ── GET /stats ────────────────────────────────────────────────
# Returns analytics data for the dashboard charts
@app.get("/stats")
def get_stats(period: str = "week", db: Session = Depends(get_db)):
    from datetime import timedelta

    all_tasks = db.query(TaskDB).all()
    today = datetime.now(timezone.utc).date()

    # Set date range based on period
    if period == "week":
        start_date = today - timedelta(days=7)
    elif period == "month":
        start_date = today - timedelta(days=30)
    else:
        start_date = None  # "all" shows everything

    # Filter tasks by due date or completed_at within the period
    def in_period(task):
        if start_date is None:
            return True
        if task.due_date:
            try:
                due = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                if due >= start_date:
                    return True
            except ValueError:
                pass
        if task.completed_at:
            try:
                completed = datetime.fromisoformat(task.completed_at).date()
                if completed >= start_date:
                    return True
            except ValueError:
                pass
        return False

    filtered_tasks = [t for t in all_tasks if in_period(t)]

    total     = len(filtered_tasks)
    completed = len([t for t in filtered_tasks if t.status == "done"])
    pending   = len([t for t in filtered_tasks if t.status == "pending"])
    in_prog   = len([t for t in filtered_tasks if t.status == "in-progress"])
    completion_rate = round((completed / total * 100), 1) if total > 0 else 0

    high_priority   = len([t for t in filtered_tasks if t.priority == "high"])
    medium_priority = len([t for t in filtered_tasks if t.priority == "medium"])
    low_priority    = len([t for t in filtered_tasks if t.priority == "low"])

    completed_by_day = {}
    for task in filtered_tasks:
        if task.completed_at:
            day = task.completed_at[:10]
            completed_by_day[day] = completed_by_day.get(day, 0) + 1

    daily_completions = [
        {"date": day, "completed": count}
        for day, count in sorted(completed_by_day.items())
    ]

    due_this_week = []
    for task in all_tasks:
        if task.due_date and task.status != "done":
            try:
                due = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                days_until_due = (due - today).days
                if 0 <= days_until_due <= 7:
                    due_this_week.append({
                        "id": task.id,
                        "title": task.title,
                        "due_date": task.due_date,
                        "priority": task.priority,
                        "days_until_due": days_until_due
                    })
            except ValueError:
                pass

    return {
        "period": period,
        "total": total,
        "completed": completed,
        "pending": pending,
        "in_progress": in_prog,
        "completion_rate": completion_rate,
        "priority_breakdown": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority
        },
        "daily_completions": daily_completions,
        "due_this_week": sorted(due_this_week, key=lambda x: x["days_until_due"])
    }
@app.get("/")
def root():
    return {
        "name": "Task Manager API",
        "version": "1.0",
        "description": "A REST API for managing tasks with priorities, due dates, and analytics",
        "author": "Akshat",
        "built_with": "Python, FastAPI, SQLAlchemy, SQLite",
        "project": "Project 4 — AI Pair-Programmed Endpoint | Himshikhar Track",
        "live_frontend": "https://task-manager-frontend-nine-silk.vercel.app",
        "interactive_docs": "https://task-manager-api-uvu0.onrender.com/docs",
        "endpoints": {
            "GET /tasks": "Get all tasks",
            "GET /tasks/{id}": "Get one task by ID",
            "POST /tasks": "Create a new task",
            "PUT /tasks/{id}": "Update a task",
            "DELETE /tasks/{id}": "Delete a task",
            "GET /stats": "Get analytics and completion stats"
        },
        "tests": "17 automated pytest tests — all passing",
        "note": "Backend hosted on Render free tier — may take 30-60 seconds to wake up after inactivity"
    }