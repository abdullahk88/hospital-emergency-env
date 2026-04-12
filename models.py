from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field
from openenv.core.env_server.types import Action, Observation, State


class PatientCase(BaseModel):
    patient_id: str
    age: int
    chief_complaint: str
    symptoms: list[str]
    vitals: dict
    arrival_step: int
    current_severity: str
    assigned_resource: Optional[str] = None


class Assignment(BaseModel):
    patient_id: str
    action_type: str
    reasoning: str


class HospitalAction(Action):
    assignments: list[Assignment] = Field(
        description="List of patient assignments for this step"
    )


class HospitalObservation(Observation):
    patients_waiting: list[PatientCase] = Field(default_factory=list)
    patients_in_treatment: list[PatientCase] = Field(default_factory=list)
    resources_available: dict = Field(default_factory=dict)
    current_step: int = 0
    task_name: str = "easy"
    feedback: Optional[str] = None


class HospitalState(State):
    episode_id: str = ""
    task_name: str = "easy"
    patients_treated: int = 0
    patients_deteriorated: int = 0
    critical_misses: int = 0
    patients_deceased: int = 0