import httpx
from typing import Optional
from models import HospitalAction, HospitalObservation


class HospitalEnvClient:

    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url.rstrip("/")
        self.session_id: Optional[str] = None
        self._client = httpx.Client(timeout=60.0)

    def reset(self, task_name: str = "easy") -> HospitalObservation:
        r = self._client.post(
            f"{self.base_url}/reset",
            json={"task_name": task_name, "session_id": self.session_id},
        )
        r.raise_for_status()
        data = r.json()
        self.session_id = data["session_id"]
        return HospitalObservation(**data["observation"])

    def step(self, action: HospitalAction) -> HospitalObservation:
        if self.session_id is None:
            raise RuntimeError("Call reset() first.")
        r = self._client.post(
            f"{self.base_url}/step",
            json={"session_id": self.session_id, "action": action.model_dump()},
        )
        r.raise_for_status()
        return HospitalObservation(**r.json()["observation"])

    def grade(self) -> float:
        if self.session_id is None:
            raise RuntimeError("Call reset() first.")
        r = self._client.post(
            f"{self.base_url}/grade",
            json={"session_id": self.session_id},
        )
        r.raise_for_status()
        return r.json()["score"]

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()