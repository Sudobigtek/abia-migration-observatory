import requests
import json
from django.conf import settings
from django.core.cache import cache

OLLAMA_BASE_URL = getattr(settings, "OLLAMA_URL", "http://localhost:11434")

def query_ollama(prompt, model="llama3", system=None, timeout=30):
    cache_key = f"ollama:{model}:{hash(prompt) % 1000000}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    if system:
        payload["system"] = system
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=timeout
        )
        resp.raise_for_status()
        data = resp.json()
        try:
            result = json.loads(data.get("response", "{}"))
        except json.JSONDecodeError:
            result = {"raw": data.get("response", ""), "parsed": False}
        cache.set(cache_key, result, timeout=3600)
        return result
    except requests.exceptions.ConnectionError:
        return {"error": "Ollama not available", "status": "offline"}
    except requests.exceptions.Timeout:
        return {"error": "Request timeout", "status": "timeout"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

def assess_migrant_risk(migrant_data):
    system_prompt = (
        "You are a migration risk assessment AI. Analyze the provided migrant data "
        "and return a JSON object with: risk_level (one of [low, medium, high, critical]), "
        "risk_score (float 0.0 to 1.0), factors (object with risk factor scores 0.0 to 1.0), "
        "recommendations (array of recommended actions). Be conservative - flag potential "
        "trafficking, exploitation, or health emergencies."
    )
    prompt = (
        f"Assess the risk for this migrant:\n"
        f"Name: {migrant_data.get(\"full_name\", \"Unknown\")}\n"
        f"Gender: {migrant_data.get(\"gender\", \"unknown\")}\n"
        f"Age: {migrant_data.get(\"age\", \"unknown\")}\n"
        f"Nationality: {migrant_data.get(\"nationality\", \"unknown\")}\n"
        f"Status: {migrant_data.get(\"status\", \"unknown\")}\n"
        f"Current LGA: {migrant_data.get(\"current_lga\", \"unknown\")}\n"
        f"Cases: {migrant_data.get(\"case_count\", 0)} open cases\n"
        f"Last updated: {migrant_data.get(\"updated_at\", \"unknown\")}\n\n"
        f"Return JSON only."
    )
    return query_ollama(prompt, system=system_prompt)

def predict_case_priority(case_data):
    system_prompt = (
        "You are a case management AI. Analyze case data and return JSON with: "
        "predicted_priority (one of [low, medium, high, critical]), confidence (float 0.0 to 1.0), "
        "reasoning (brief explanation), sla_hours (recommended response time)."
    )
    prompt = (
        f"Case: {case_data.get(\"case_type\", \"unknown\")}\n"
        f"Description: {case_data.get(\"description\", "")[:500]}\n"
        f"Migrant status: {case_data.get(\"migrant_status\", \"unknown\")}\n"
        f"Days open: {case_data.get(\"days_open\", 0)}\n\n"
        f"Return JSON only."
    )
    return query_ollama(prompt, system=system_prompt)
