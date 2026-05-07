"""
Prepares training data for Gemma 4 4B fine-tuning.
Downloads ChatDoctor-HealthCareMagic-100k and formats for structured JSON triage output.

Run in Kaggle notebook BEFORE train.py:
    pip install datasets
    python finetuning/prepare_dataset.py
"""
from datasets import load_dataset
import json
import random

SYSTEM_PROMPT = """You are a medical triage assistant for ASHA community health workers in rural India.
Given a symptom description, output ONLY a valid JSON triage assessment.

Required format:
{
  "conditions": ["condition1", "condition2"],
  "urgency": "Monitor at Home",
  "next_steps": ["step1", "step2", "step3"],
  "red_flags": ["flag1", "flag2"],
  "asha_note": "One sentence for the ASHA worker."
}

urgency must be exactly: "Monitor at Home", "Visit PHC", or "Emergency Referral"
Respond ONLY with JSON. No other text."""

# Gemma 4 chat template
GEMMA_CHAT_TEMPLATE = "<start_of_turn>user\n{system}\n\nSymptoms: {question}<end_of_turn>\n<start_of_turn>model\n{answer}<end_of_turn>"

EMERGENCY_KEYWORDS = ["emergency", "immediately", "severe", "critical", "hospital", "call 911", "serious"]
PHC_KEYWORDS = ["consult", "doctor", "physician", "clinic", "examination", "test", "check"]


def classify_urgency(answer_text):
    lower = answer_text.lower()
    if any(k in lower for k in EMERGENCY_KEYWORDS):
        return "Emergency Referral"
    if any(k in lower for k in PHC_KEYWORDS):
        return "Visit PHC"
    return "Monitor at Home"


def build_structured_answer(question, answer):
    urgency = classify_urgency(answer)
    condition_name = question.replace("What is ", "").replace("How to treat ", "").replace("?", "").strip()
    if len(condition_name) > 60:
        condition_name = condition_name[:60]

    structured = {
        "conditions": [condition_name.title()],
        "urgency": urgency,
        "next_steps": [
            "Monitor patient's symptoms closely",
            "Keep patient hydrated and comfortable",
            "Schedule follow-up in 24-48 hours if no improvement"
        ],
        "red_flags": [
            "Symptoms worsen suddenly or rapidly",
            "Difficulty breathing or loss of consciousness"
        ],
        "asha_note": f"Follow up with patient within 48 hours. Urgency level: {urgency}."
    }
    return json.dumps(structured)


def prepare_and_save():
    print("Loading ChatDoctor-HealthCareMagic-100k dataset...")
    dataset = load_dataset("lavita/ChatDoctor-HealthCareMagic-100k", split="train")

    formatted = []
    for item in dataset.select(range(8000)):
        question = item.get("input", "").strip()
        answer = item.get("output", "").strip()
        if len(question) < 15 or len(answer) < 30:
            continue
        answer_json = build_structured_answer(question, answer)
        text = GEMMA_CHAT_TEMPLATE.format(
            system=SYSTEM_PROMPT, question=question, answer=answer_json
        )
        formatted.append({"text": text})

    random.seed(42)
    random.shuffle(formatted)
    train = formatted[:5000]
    val = formatted[5000:5800]

    with open("train_data.jsonl", "w") as f:
        for item in train:
            f.write(json.dumps(item) + "\n")
    with open("val_data.jsonl", "w") as f:
        for item in val:
            f.write(json.dumps(item) + "\n")

    print(f"Prepared {len(train)} train and {len(val)} validation samples.")
    print("Saved: train_data.jsonl, val_data.jsonl")


if __name__ == "__main__":
    prepare_and_save()
