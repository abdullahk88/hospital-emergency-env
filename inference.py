import os
import json
import sys
from openai import OpenAI
from models import HospitalAction, Assignment

API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
ENV_BASE_URL = os.environ.get("ENV_BASE_URL")
ENV_NAME = "hospital-emergency-env"

if not HF_TOKEN:
    print("[WARN] HF_TOKEN not set — LLM calls will use fallback mode", file=sys.stderr, flush=True)

client = OpenAI(api_key=HF_TOKEN or "placeholder", base_url=API_BASE_URL)

_USE_EMBEDDED = ENV_BASE_URL is None

if _USE_EMBEDDED:
    from server.hospital_environment import HospitalEnvironment

    class _EmbeddedClient:
        def __init__(self):
            self._env = None

        def reset(self, task_name="easy"):
            self._env = HospitalEnvironment(task_name=task_name)
            return self._env.reset()

        def step(self, action):
            return self._env.step(action)

        def grade(self):
            return self._env.grade_episode()

        def close(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

else:
    from client import HospitalEnvClient


def _make_client():
    if _USE_EMBEDDED:
        return _EmbeddedClient()
    return HospitalEnvClient(base_url=ENV_BASE_URL)


def build_prompt(observation) -> str:
    waiting = observation.patients_waiting
    resources = observation.resources_available

    patients_text = ""
    for p in waiting:
        patients_text += (
            f"\n- ID: {p.patient_id} | Age: {p.age} | Severity: {p.current_severity}"
            f"\n  Complaint: {p.chief_complaint}"
            f"\n  Symptoms: {', '.join(p.symptoms)}"
            f"\n  Vitals: BP={p.vitals.get('bp')} HR={p.vitals.get('hr')} "
            f"Temp={p.vitals.get('temp')} SpO2={p.vitals.get('spo2')}\n"
        )

    return f"""You are an ER doctor. Triage the following patients.

Resources available: ICU beds={resources.get('icu_beds', 0)}, Doctors={resources.get('doctors', 0)}, Ventilators={resources.get('ventilators', 0)}
Last feedback: {observation.feedback}

Patients waiting:
{patients_text}
For each patient choose: assign_icu, assign_ventilator, assign_doctor, defer, or discharge.
Reply with ONLY a JSON array:
[{{"patient_id": "P001", "action_type": "assign_icu", "reasoning": "critical chest pain"}}]"""


def call_llm(prompt: str):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=1000,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are an ER triage doctor. Respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip()), None
    except Exception as e:
        return [], str(e).replace("\n", " ")[:200]


def run_episode(env_client, task_name: str) -> dict:
    observation = env_client.reset(task_name=task_name)

    print(f"[START] task={task_name} env={ENV_NAME} model={MODEL_NAME}", flush=True)

    step_rewards = []
    step_num = 0
    last_error = None

    while not observation.done:
        step_num += 1
        prompt = build_prompt(observation)
        raw_assignments, error = call_llm(prompt)
        last_error = error

        if raw_assignments:
            assignments = [
                Assignment(
                    patient_id=a.get("patient_id", ""),
                    action_type=a.get("action_type", "defer"),
                    reasoning=a.get("reasoning", ""),
                )
                for a in raw_assignments
                if a.get("patient_id")
            ]
        else:
            assignments = [
                Assignment(
                    patient_id=p.patient_id,
                    action_type="defer",
                    reasoning="fallback",
                )
                for p in observation.patients_waiting
            ]

        action = HospitalAction(assignments=assignments)
        action_str = json.dumps([
            {"patient_id": a.patient_id, "action_type": a.action_type}
            for a in assignments
        ]).replace(" ", "")

        observation = env_client.step(action)
        reward = observation.reward
        step_rewards.append(reward)

        done_str = "true" if observation.done else "false"
        error_str = last_error if last_error else "null"

        print(f"[STEP] step={step_num} action={action_str} reward={reward:.2f} done={done_str} error={error_str}", flush=True)

    final_score = max(0.01, min(0.99, env_client.grade()))
    success_str = "true" if final_score > 0.01 else "false"
    score_str = f"{final_score:.4f}"
    rewards_str = ",".join(f"{max(0.01, min(0.99, r)):.2f}" for r in step_rewards) if step_rewards else "0.01"

    print(f"[END] success={success_str} steps={step_num} score={score_str} rewards={rewards_str}", flush=True)

    return {"task": task_name, "final_score": final_score}


def main():
    results = []
    env_client = _make_client()

    for task_name in ["easy", "medium", "hard"]:
        try:
            result = run_episode(env_client, task_name)
            results.append(result)
        except Exception as e:
            print(f"[END] success=false steps=0 score=0.0100 rewards=0.01", flush=True)
            print(f"[ERROR] task={task_name} error={str(e)}", file=sys.stderr, flush=True)

    env_client.close()

    avg = round(sum(r["final_score"] for r in results) / len(results), 4) if results else 0.01
    print(f"[SUMMARY] average_score={avg}", flush=True)


if __name__ == "__main__":
    main()