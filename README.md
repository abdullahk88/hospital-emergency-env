---
title: Hospital Emergency Resource Allocation Environment
emoji: 🏥
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
tags:
  - openenv
  - real-world
  - healthcare
  - triage
  - resource-allocation
  - reinforcement-learning
---

# 🏥 Hospital Emergency Resource Allocation Environment

An OpenEnv-compliant RL environment where an AI agent acts as an ER doctor, triaging patients and allocating scarce hospital resources under time pressure and resource constraints.

## Overview

This environment simulates a real hospital emergency room. The agent receives a queue of patients with symptoms, vitals, and severity levels, and must allocate limited resources — ICU beds, doctors, and ventilators — optimally across multiple patients per step.

The environment models three core challenges of real hospital operations:

- Triage accuracy: assigning the right resource to the right patient
- Resource constraints: allocating scarce beds and staff under pressure
- Dynamic evolution: new patients arrive, conditions deteriorate, untreated critical patients die

## Action Space

```json
{
  "assignments": [
    {
      "patient_id": "P001",
      "action_type": "assign_icu",
      "reasoning": "Critical chest pain with low BP"
    }
  ]
}
```

Valid action types: `assign_icu`, `assign_ventilator`, `assign_doctor`, `defer`, `discharge`

## Observation Space

| Field                   | Type  | Description                              |
| ----------------------- | ----- | ---------------------------------------- |
| `patients_waiting`      | list  | Patients awaiting assignment             |
| `patients_in_treatment` | list  | Patients currently assigned              |
| `resources_available`   | dict  | Remaining ICU beds, doctors, ventilators |
| `current_step`          | int   | Current step number                      |
| `task_name`             | str   | easy / medium / hard                     |
| `feedback`              | str   | Result of last action                    |
| `reward`                | float | Step reward                              |
| `done`                  | bool  | Episode complete                         |

## Tasks

### 🟢 Easy

5 patients, unlimited resources. Pure triage accuracy test.
Expected LLM score: ~0.75 | Random baseline: ~0.20

### 🟡 Medium

10 patients, limited resources: ICU=3, Doctors=5, Ventilators=2.
Agent must allocate optimally under hard constraints.
Expected LLM score: ~0.45 | Random baseline: ~0.10

### 🔴 Hard

15 patients, all resources constrained. New patients arrive at step 3. Patient conditions deteriorate every 2 steps. Critical patients ignored for 3+ steps die — triggering a -1.0 penalty.
Expected LLM score: ~0.25 | Random baseline: ~0.05

## Reward Function

Dense rewards at every step:

| Situation                   | Reward       |
| --------------------------- | ------------ |
| Correct resource assignment | +0.6         |
| Acceptable but suboptimal   | +0.2         |
| Critical patient deferred   | -0.3 to -0.5 |
| Resource over-allocated     | -0.1         |
| Patient death (hard task)   | -1.0         |

All rewards clamped to [0.0, 1.0].

## Setup

### Run locally

```bash
git clone https://huggingface.co/spaces/AbdullahK8/hospital-emergency-env
cd hospital-emergency-env
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### Run with Docker

```bash
docker build -t hospital-emergency-env .
docker run -p 7860:7860 hospital-emergency-env
```

### Run inference

```bash
export HF_TOKEN=your_token
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
export ENV_BASE_URL=https://abdullahk8-hospital-emergency-env.hf.space
python inference.py
```

## Project Structure

```
hospital-emergency-env/
├── server/
│   ├── __init__.py
│   ├── hospital_environment.py
│   └── app.py
├── models.py
├── tasks.py
├── graders.py
├── client.py
├── inference.py
├── openenv.yaml
├── pyproject.toml
├── Dockerfile
└── requirements.txt
```
