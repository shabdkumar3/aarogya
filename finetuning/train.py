"""
Fine-tunes Gemma 4 4B using Unsloth + QLoRA.
Run in Kaggle notebook with GPU T4 x2 enabled.
Runtime: ~45-90 minutes for 300 steps.

Setup:
    pip install unsloth trl transformers datasets torch bitsandbytes
    python finetuning/prepare_dataset.py   # generate train/val data first
    python finetuning/train.py
"""
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset
import torch

MAX_SEQ_LENGTH = 2048
LOAD_IN_4BIT = True

# Load Gemma 4 4B via Unsloth
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/gemma-4-4b-it",   # Gemma 4 4B instruction-tuned
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=LOAD_IN_4BIT,
)

# Add QLoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=42,
)

print(f"Trainable parameters: {model.print_trainable_parameters()}")

dataset = load_dataset("json", data_files={"train": "train_data.jsonl", "validation": "val_data.jsonl"})

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=2,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        max_steps=300,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=10,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        seed=42,
        output_dir="training_outputs",
        eval_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=100,
        report_to="none",
    ),
)

print("Starting Gemma 4 fine-tuning with Unsloth QLoRA...")
trainer_stats = trainer.train()
print(f"Training complete. Time: {trainer_stats.metrics['train_runtime']:.0f}s")

model.save_pretrained("aarogya_gemma4_finetuned")
tokenizer.save_pretrained("aarogya_gemma4_finetuned")
print("Saved to: aarogya_gemma4_finetuned/")

# Uncomment to push to Hugging Face Hub:
# from huggingface_hub import login
# login(token="your_hf_token")
# model.push_to_hub("your-username/aarogya-gemma4-4b")
# tokenizer.push_to_hub("your-username/aarogya-gemma4-4b")
