"""
Ablation: Base Gemma 4 4B vs fine-tuned Aarogya Gemma 4 4B.
Run after train.py. Copy the output table into your Kaggle write-up.
"""
from unsloth import FastLanguageModel
import json

TEST_CASES = [
    {"input": "Child has high fever 103F for 3 days, rash spreading on chest", "expected_urgency": "Visit PHC"},
    {"input": "Elderly man has crushing chest pain and left arm pain, sweating heavily", "expected_urgency": "Emergency Referral"},
    {"input": "Small cut on palm, bleeding has stopped, no swelling or redness", "expected_urgency": "Monitor at Home"},
    {"input": "Patient with diabetes, blood sugar over 400, feeling dizzy and confused", "expected_urgency": "Emergency Referral"},
    {"input": "Mild dry cough for 2 days, no fever, eating and drinking normally", "expected_urgency": "Monitor at Home"},
    {"input": "Pregnant woman in 8th month, severe headache and swollen feet", "expected_urgency": "Emergency Referral"},
    {"input": "Child refusing to eat for 2 days with mild fever of 100F", "expected_urgency": "Visit PHC"},
]

SYSTEM_PROMPT = """You are a medical triage assistant. Output ONLY valid JSON.
Required format: {"conditions": [], "urgency": "Monitor at Home", "next_steps": [], "red_flags": [], "asha_note": ""}
urgency must be exactly: "Monitor at Home", "Visit PHC", or "Emergency Referral" """


def load_model(model_path):
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_path, max_seq_length=2048, load_in_4bit=True
    )
    FastLanguageModel.for_inference(model)
    return model, tokenizer


def infer(model, tokenizer, symptom_text):
    prompt = f"<start_of_turn>user\n{SYSTEM_PROMPT}\n\nSymptoms: {symptom_text}<end_of_turn>\n<start_of_turn>model\n"
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.1, do_sample=False)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "<start_of_turn>model" in text:
        text = text.split("<start_of_turn>model")[-1].strip()
    try:
        return json.loads(text)
    except:
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        return {"urgency": "PARSE_ERROR", "raw": text[:200]}


def evaluate():
    print("Loading base model (unsloth/gemma-4-4b-it)...")
    base_model, base_tok = load_model("unsloth/gemma-4-4b-it")

    print("Loading fine-tuned Aarogya model...")
    ft_model, ft_tok = load_model("aarogya_gemma4_finetuned")

    print("\n" + "="*80)
    print("ABLATION: Base Gemma 4 4B  vs  Aarogya Fine-tuned Gemma 4 4B")
    print("="*80)

    base_correct = ft_correct = base_valid = ft_valid = 0

    for i, case in enumerate(TEST_CASES):
        print(f"\n[{i+1}/{len(TEST_CASES)}] {case['input'][:70]}...")
        br = infer(base_model, base_tok, case['input'])
        fr = infer(ft_model, ft_tok, case['input'])

        bc = br.get('urgency') == case['expected_urgency']
        fc = fr.get('urgency') == case['expected_urgency']
        bv = 'conditions' in br and 'next_steps' in br
        fv = 'conditions' in fr and 'next_steps' in fr

        if bc: base_correct += 1
        if fc: ft_correct += 1
        if bv: base_valid += 1
        if fv: ft_valid += 1

        print(f"  Expected:   {case['expected_urgency']}")
        print(f"  Base:       {br.get('urgency')} {'✅' if bc else '❌'} | JSON valid: {'✅' if bv else '❌'}")
        print(f"  Fine-tuned: {fr.get('urgency')} {'✅' if fc else '❌'} | JSON valid: {'✅' if fv else '❌'}")

    n = len(TEST_CASES)
    print("\n" + "="*80)
    print(f"{'Metric':<35} {'Base Gemma 4 4B':<20} {'Aarogya 4B':<15}")
    print("-"*70)
    print(f"{'Correct urgency':<35} {base_correct}/{n} ({base_correct/n*100:.0f}%)        {ft_correct}/{n} ({ft_correct/n*100:.0f}%)")
    print(f"{'Valid JSON output':<35} {base_valid}/{n} ({base_valid/n*100:.0f}%)        {ft_valid}/{n} ({ft_valid/n*100:.0f}%)")
    print("="*80)
    print("\nCopy this table into your Kaggle write-up fine-tuning section.")


if __name__ == "__main__":
    evaluate()
