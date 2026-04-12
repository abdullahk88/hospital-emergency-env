from __future__ import annotations
import uuid
import copy
from typing import Optional
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State
from models import HospitalAction, HospitalObservation, HospitalState, PatientCase
from tasks import (
    EASY_PATIENTS, MEDIUM_PATIENTS, MEDIUM_RESOURCES,
    HARD_INITIAL_PATIENTS, HARD_ARRIVING_PATIENTS, HARD_RESOURCES,
)
from graders import grade_easy, grade_medium, grade_hard


class HospitalEnvironment(Environment):

    SUPPORTS_CONCURRENT_SESSIONS = True
    MAX_STEPS = {"easy": 3, "medium": 5, "hard": 8}

    def __init__(self, task_name: str = "easy"):
        assert task_name in ("easy", "medium", "hard")
        self.task_name = task_name
        self._state = HospitalState(
            episode_id=str(uuid.uuid4()),
            task_name=task_name,
            patients_treated=0,
            patients_deteriorated=0,
            critical_misses=0,
            patients_deceased=0,
        )
        self.patients_waiting: list[dict] = []
        self.patients_in_treatment: list[dict] = []
        self.resources_available: dict = {}
        self.episode_actions: list[dict] = []
        self.step_count: int = 0

    def reset(self) -> HospitalObservation:
        self.step_count = 0
        self.episode_actions = []
        self._state = HospitalState(
            episode_id=str(uuid.uuid4()),
            task_name=self.task_name,
            patients_treated=0,
            patients_deteriorated=0,
            critical_misses=0,
            patients_deceased=0,
        )

        if self.task_name == "easy":
            self.patients_waiting = copy.deepcopy(EASY_PATIENTS)
            self.resources_available = {"icu_beds": 99, "doctors": 99, "ventilators": 99}
        elif self.task_name == "medium":
            self.patients_waiting = copy.deepcopy(MEDIUM_PATIENTS)
            self.resources_available = copy.deepcopy(MEDIUM_RESOURCES)
        elif self.task_name == "hard":
            self.patients_waiting = copy.deepcopy(HARD_INITIAL_PATIENTS)
            self.resources_available = copy.deepcopy(HARD_RESOURCES)

        self.patients_in_treatment = []
        return self._build_obs(reward=0.0, done=False, feedback="Episode started.")

    def step(self, action: HospitalAction) -> HospitalObservation:
        self.step_count += 1
        reward = 0.0
        feedback_parts = []

        for assignment in action.assignments:
            pid = assignment.patient_id
            action_type = assignment.action_type

            patient = self._find_patient(pid, self.patients_waiting)
            if patient is None:
                feedback_parts.append(f"Patient {pid} not found.")
                continue

            self.episode_actions.append({
                "patient_id": pid,
                "action_type": action_type,
                "step_number": self.step_count,
            })

            step_reward, fb = self._evaluate(patient, action_type)
            reward += step_reward
            feedback_parts.append(fb)

            if action_type in ("assign_icu", "assign_doctor", "assign_ventilator"):
                rkey = self._resource_key(action_type)
                if rkey and self.resources_available.get(rkey, 0) > 0:
                    patient["assigned_resource"] = action_type
                    self.patients_waiting.remove(patient)
                    self.patients_in_treatment.append(patient)
                    self.resources_available[rkey] -= 1
                    self._state.patients_treated += 1
                else:
                    feedback_parts.append(f"Resource {action_type} full.")
                    reward -= 0.1

            elif action_type == "defer":
                if patient.get("current_severity") == "critical":
                    self._state.critical_misses += 1
                    reward -= 0.3
                    feedback_parts.append(f"DANGER: Critical patient {pid} deferred!")
                else:
                    feedback_parts.append(f"Patient {pid} deferred.")

            elif action_type == "discharge":
                treated = self._find_patient(pid, self.patients_in_treatment)
                if treated:
                    rkey = self._resource_key(treated.get("assigned_resource", ""))
                    if rkey:
                        self.resources_available[rkey] += 1
                    self.patients_in_treatment.remove(treated)
                    feedback_parts.append(f"Patient {pid} discharged.")

        if self.task_name == "hard" and self.step_count == 3:
            arrivals = copy.deepcopy(HARD_ARRIVING_PATIENTS)
            self.patients_waiting.extend(arrivals)
            feedback_parts.append(f"🚨 {len(arrivals)} new patients arrived!")

        if self.task_name == "hard" and self.step_count % 2 == 0:
            deteriorated = self._deteriorate()
            if deteriorated:
                self._state.patients_deteriorated += 1
                feedback_parts.append(f"⚠️ Patient {deteriorated} worsened!")

        if self.task_name == "hard":
            dead = []
            for p in self.patients_waiting:
                if p.get("current_severity") == "critical":
                    if self.step_count - p.get("arrival_step", 0) >= 3:
                        dead.append(p)
            for p in dead:
                self.patients_waiting.remove(p)
                self._state.patients_deceased += 1
                self._state.critical_misses += 1
                reward -= 1.0
                feedback_parts.append(f"💀 Patient {p['patient_id']} died — untreated too long!")

        reward = round(max(0.01, min(0.99, reward)), 4)
        done = self._check_done()
        return self._build_obs(reward=reward, done=done, feedback=" | ".join(feedback_parts) or "Step processed.")

    @property
    def state(self) -> HospitalState:
        return self._state

    def grade_episode(self) -> float:
        if self.task_name == "easy":
            return grade_easy(self.episode_actions)
        elif self.task_name == "medium":
            return grade_medium(self.episode_actions)
        return grade_hard(self.episode_actions)

    def _build_obs(self, reward: float, done: bool, feedback: str) -> HospitalObservation:
        return HospitalObservation(
            reward=reward,
            done=done,
            patients_waiting=[PatientCase(**p) for p in self.patients_waiting],
            patients_in_treatment=[PatientCase(**p) for p in self.patients_in_treatment],
            resources_available=dict(self.resources_available),
            current_step=self.step_count,
            task_name=self.task_name,
            feedback=feedback,
        )

    def _find_patient(self, pid: str, lst: list) -> Optional[dict]:
        for p in lst:
            if p["patient_id"] == pid:
                return p
        return None

    def _evaluate(self, patient: dict, action_type: str):
        severity = patient.get("current_severity", "minor")
        pid = patient["patient_id"]
        ideal = {
            "critical": ["assign_icu", "assign_ventilator"],
            "serious": ["assign_doctor"],
            "moderate": ["assign_doctor"],
            "minor": ["defer"],
        }
        ideal_actions = ideal.get(severity, ["defer"])
        if action_type in ideal_actions:
            return 0.6, f"✅ {pid} ({severity}) → {action_type}"
        elif action_type == "defer" and severity == "critical":
            return -0.4, f"❌ {pid} critical patient deferred!"
        elif action_type in ("assign_icu", "assign_ventilator") and severity == "minor":
            return -0.1, f"⚠️ {pid} minor patient given intensive resource"
        else:
            return 0.2, f"🟡 {pid} ({severity}) acceptable → {action_type}"

    def _resource_key(self, action_type: str) -> Optional[str]:
        return {"assign_icu": "icu_beds", "assign_doctor": "doctors", "assign_ventilator": "ventilators"}.get(action_type)

    def _deteriorate(self) -> Optional[str]:
        deterioration_map = {"minor": "moderate", "moderate": "serious", "serious": "critical"}
        eligible = [p for p in self.patients_waiting if p["current_severity"] in deterioration_map]
        if not eligible:
            return None
        victim = sorted(eligible, key=lambda x: x["patient_id"])[0]
        victim["current_severity"] = deterioration_map[victim["current_severity"]]
        return victim["patient_id"]

    def _check_done(self) -> bool:
        if self.step_count >= self.MAX_STEPS.get(self.task_name, 5):
            return True
        if self.task_name != "hard" and len(self.patients_waiting) == 0:
            return True
        return False