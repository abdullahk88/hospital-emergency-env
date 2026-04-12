import sys
import os
import uuid
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import HospitalAction, HospitalObservation, HospitalState
from server.hospital_environment import HospitalEnvironment

app = FastAPI(title="Hospital Emergency Resource Allocation Environment", version="0.1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

sessions: dict[str, HospitalEnvironment] = {}


class ResetRequest(BaseModel):
    task_name: str = "easy"
    session_id: Optional[str] = None


class StepRequest(BaseModel):
    session_id: str
    action: HospitalAction


class StateRequest(BaseModel):
    session_id: str


class GradeRequest(BaseModel):
    session_id: str


@app.get("/health")
def health():
    return {"status": "healthy", "environment": "hospital-emergency-env"}


@app.post("/reset")
def reset(request: Optional[ResetRequest] = None):
    if request is None:
        request = ResetRequest()
    session_id = request.session_id or str(uuid.uuid4())
    env = HospitalEnvironment(task_name=request.task_name)
    observation = env.reset()
    sessions[session_id] = env
    return {"session_id": session_id, "observation": observation.model_dump()}


@app.post("/step")
def step(request: StepRequest):
    env = sessions.get(request.session_id)
    if env is None:
        raise HTTPException(status_code=404, detail="Session not found. Call /reset first.")
    observation = env.step(request.action)
    return {"session_id": request.session_id, "observation": observation.model_dump()}


@app.post("/state")
def state(request: StateRequest):
    env = sessions.get(request.session_id)
    if env is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"session_id": request.session_id, "state": env.state.model_dump()}


@app.post("/grade")
def grade(request: GradeRequest):
    env = sessions.get(request.session_id)
    if env is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"session_id": request.session_id, "score": env.grade_episode()}


@app.get("/tasks")
def list_tasks():
    return {"tasks": [
        {"name": "easy", "description": "5 patients, unlimited resources.", "max_steps": 3, "difficulty": "easy"},
        {"name": "medium", "description": "10 patients, limited resources (ICU=3, doctors=5, ventilators=2).", "max_steps": 5, "difficulty": "medium"},
        {"name": "hard", "description": "15 patients, constrained resources, new arrivals, deterioration, death mechanic.", "max_steps": 8, "difficulty": "hard"},
    ]}


def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()