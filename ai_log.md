# AI Collaboration Log — Task Manager API
## Mini Project : Building Restful API with AI
**Student**: Akshat Dad
**Roll Number**: 333
**Course**: Himshikhar Track — Software Development with AI 

---

## Project Overview

Built a full-stack Task Manager application using Python (FastAPI) as the backend and React as the frontend. The backend includes 6 REST API endpoints, a real SQLite database, input validation, an analytics/stats endpoint, and 17 automated pytest tests. The frontend includes task management UI, priority/due date editing, and an analytics dashboard with pie charts, bar charts, and weekly/monthly filtering.

Both are deployed live:
- **Backend API**: https://task-manager-api-uvu0.onrender.com
- **Frontend:** https://task-manager-frontend-nine-silk.vercel.app

---

## AI Tool Used

**Claude (Anthropic)** — used throughout the project for code generation, debugging, explanation, and file writing.

---

## Prompts Used and Results

### Basic FastAPI setup
**Prompt:** "Create a minimal FastAPI app with one GET /tasks route"

**What AI got right:**
- Correct FastAPI app structure and syntax
- Route decorator `@app.get("/tasks")` used correctly
- Returned a Python list that FastAPI auto-converted to JSON
- Generated 3 working pytest tests using TestClient on first try

**What I had to fix:**
- AI did not warn that `uvicorn` command doesn't work directly on Windows PowerShell — had to use `python -m uvicorn main:app --reload` instead
- AI did not mention needing to `cd` into the correct project folder before running the server — got "Could not import module main" error
- `StarletteDeprecationWarning` about httpx appeared in test output — AI did not mention this would happen, though tests still passed

---

### — Full CRUD API + Pydantic models
**Prompt:** "Add a Pydantic model for Task and build GET, POST, PUT, DELETE endpoints"

**What AI got right:**
- Correctly split into two Pydantic models: `TaskCreate` (no id, for input) and `TaskResponse` (with id, for output)
- Used `HTTPException` with correct 404 status codes
- Used `status_code=201` on POST — more accurate than 200
- Used `enumerate()` correctly in DELETE to find index
- Generated `setup_function()` in tests to reset state before each test — important pattern AI got right without being asked
- All 18 tests passed on first run

**What I had to fix:**
- Nothing major — this was the smoothest part of the project

---

### — SQLite + SQLAlchemy
**Prompt:** "Replace the in-memory list with a real SQLite database using SQLAlchemy"

**What AI got right:**
- Correct `database.py` structure with engine, SessionLocal, Base, and `get_db` dependency
- Used `Depends(get_db)` correctly in all route functions
- Used a separate test database (`test.db`) for pytest so real data is never touched during testing
- `db.commit()` and `db.refresh()` used correctly after every write operation

**What I had to fix:**
- `database.py` was accidentally created as an empty file (0 bytes) — the file write didn't execute properly in VS Code. Had to rewrite it manually
- Old `tasks.db` had the old schema without new columns — SQLAlchemy doesn't auto-migrate existing tables, had to delete and recreate the database file
- Special characters in code comments (`─`) got corrupted to `â"€â"€` during copy-paste on Windows — caused syntax errors. Had to use PowerShell `Set-Content` commands to write files cleanly

---

### — CORS fix : connecting React to FastAPI
**Prompt:** "Add CORS middleware so my React frontend can talk to the FastAPI backend"

**What AI got right:**
- Correctly identified `CORSMiddleware` from `fastapi.middleware.cors`
- Correct placement — middleware must be added before routes

**What I had to fix:**
- AI added CORS correctly in the code but the file wasn't saved properly in VS Code — the change didn't reach GitHub so Render kept serving the old version
- Had to force a "Clear build cache & deploy" on Render to pick up the fix
- `OPTIONS /tasks HTTP/1.1" 405 Method Not Allowed` appeared in Render logs — a browser preflight check that AI didn't explain upfront, though it resolved after the clean redeploy

---

### — New Fields : priority, due_date, completed_at
**Prompt:** "Add priority, due_date, and completed_at fields to the Task model"

**What AI got right:**
- `completed_at` auto-set when status changes to "done" — smart business logic
- `completed_at` cleared when status changed back from "done" — edge case handled correctly
- Pydantic validators for status and priority that reject invalid values with clear error messages

**What I had to fix:**
- Copy-paste corruption of special characters kept breaking `main.py` and `models.py` — had to use PowerShell `Set-Content` to write files directly from terminal
- Python 3.14 was installed alongside Python 3.13 — packages weren't available in the new version, had to reinstall with `pip install` for Python 3.14

---

### Stats endpoint and dashboard
**Prompt:** "Build a /stats endpoint that returns completion rates, daily completions, priority breakdown, and tasks due this week"

**What AI got right:**
- Correct structure for analytics — grouped completions by day using dictionary, sorted output
- `due_this_week` correctly filtered tasks with due dates within 7 days
- Period filter (`?period=week`, `?period=month`, `?period=all`) implemented cleanly with a single `start_date` calculation

**What I had to fix:**
- Nothing significant — stats endpoint worked correctly on first run

---

### React frontend
**Prompt:** "Build a React frontend with separate components for AddTask, TaskCard, TaskList, and Dashboard"

**What AI got right:**
- Clean component separation — each file had one responsibility
- `useEffect` with dependency array `[period]` — re-fetches stats when toggle changes
- Recharts integration (PieChart, BarChart, ResponsiveContainer) — worked correctly
- Color-coded priority dropdowns on TaskCard

**What I had to fix:**
- `Dashboard.js` was not placed in the correct folder initially — caused "Module not found" error
- `date` input showed `dd-mm-yyyy` placeholder from browser — AI didn't explain this is Windows/browser regional behavior, not a code bug. Fixed by adding a label "Due Date (dd-mm-yyyy)" above the input
- Past dates were not blocked on the date picker — added `min={today}` to fix

---

## Summary — Where AI Helped vs Where I Corrected

| Area | AI Performance |
|------|---------------|
| FastAPI route structure | Excellent — correct on first try |
| Pydantic models | Excellent — two-model pattern was right |
| pytest tests | Excellent — all passed on first run |
| SQLAlchemy setup | Good — minor file-writing issues |
| CORS middleware | Good — correct code, deployment confusion |
| Input validation | Excellent — validators worked perfectly |
| React components | Good — component structure was clean |
| Windows-specific issues | Poor — AI consistently did not warn about PowerShell differences, PATH issues, or copy-paste encoding problems |

---

## Key Corrections Made

1. **`python -m uvicorn`** instead of `uvicorn` — Windows PowerShell doesn't recognize uvicorn directly
2. **`cd` into project folder** before running server — AI assumed terminal was already in the right place
3. **Delete `tasks.db`** after schema changes — SQLAlchemy doesn't auto-migrate
4. **PowerShell `Set-Content`** to write files — copy-paste corrupted special characters in comments
5. **`min={today}`** on date inputs — AI didn't add past-date blocking
6. **Force Render redeploy** — AI didn't warn that Render caches old builds
7. **Reinstall packages for Python 3.14** — AI didn't account for multiple Python versions on Windows

---

## What I Learned About AI-Assisted Development

**AI is excellent at:**
- Boilerplate and standard patterns (routes, models, tests)
- Knowing the right library functions and how to combine them
- Generating test cases that cover edge cases
- Explaining concepts when asked

**AI consistently missed:**
- Windows-specific environment issues (PowerShell vs bash)
- Multi-Python-version conflicts
- File encoding issues during copy-paste on Windows
- Deployment-specific behavior (Render caching, free tier sleep)
- Browser-specific UI behavior (date input placeholders)

**Conclusion:** AI dramatically sped up development — what might have taken weeks was built in days. But it required a human to handle environment setup, deployment troubleshooting, and platform-specific issues. AI writes the code; a developer makes it actually run.