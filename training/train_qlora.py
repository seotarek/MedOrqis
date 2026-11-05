#!/usr/bin/env python3
"""
MedOrqis Foundation Model — QLoRA Fine-Tuning Pipeline
Trained on RunPod / Cloud GPU (Zero local download overhead).

Targets:
- Applied-Innovation-Center/Karnak-40B-v1.0 (MoE, 81.4 GB BF16 -> 24 GB 4-bit NF4)
- Or Applied-Innovation-Center/Karnak-6B-v1.0 (Dense, 12 GB BF16 -> 4 GB 4-bit NF4)

Features:
- BitsAndBytes 4-bit NF4 Quantization + Double Quant
- PEFT LoRA (r=16, alpha=32, target_modules for Qwen/MoE attention & MLP)
- Gradient Checkpointing & FlashAttention-2
- Direct push of trained LoRA adapters to Hugging Face Hub (seotarek/medorqis-karnak-40b-lora)
"""

import os
import sys
import argparse
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

def _load_env_file():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v

_load_env_file()
HF_TOKEN = os.getenv("HF_TOKEN", "")
DEFAULT_MODEL_ID = "Applied-Innovation-Center/Karnak-40B-v1.0"
DEFAULT_OUTPUT_REPO = "seotarek/medorqis-karnak-40b-lora"


def parse_args():
    parser = argparse.ArgumentParser(description="MedOrqis QLoRA Fine-Tuning")
    parser.add_argument("--model_id", type=str, default=DEFAULT_MODEL_ID, help="Base foundation model ID on Hugging Face")
    parser.add_argument("--output_repo", type=str, default=DEFAULT_OUTPUT_REPO, help="Target Hugging Face Hub repository for LoRA weights")
    parser.add_argument("--dataset_path", type=str, default="training/medorqis_clinical_instructions.jsonl", help="Local or HF dataset path")
    parser.add_argument("--num_train_epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=2, help="Per-device batch size")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=8, help="Gradient accumulation steps")
    parser.add_argument("--learning_rate", type=float, default=2e-4, help="Peak learning rate")
    parser.add_argument("--max_seq_length", type=int, default=2048, help="Maximum sequence length")
    parser.add_argument("--lora_r", type=int, default=16, help="LoRA rank")
    parser.add_argument("--lora_alpha", type=int, default=32, help="LoRA alpha scaling factor")
    return parser.parse_args()


def format_chatml_prompt(example, tokenizer):
    """Formats messages into ChatML string using tokenizer's native chat template."""
    messages = example.get("messages", [])
    tools = example.get("tools", None)
    
    try:
        # Use native chat template with tools if supported
        formatted = tokenizer.apply_chat_template(
            messages,
            tools=tools,
            tokenize=False,
            add_generation_prompt=False
        )
    except Exception:
        # Fallback to standard messages
        formatted = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
    return {"text": formatted}


def main():
    args = parse_args()
    print("=" * 70)
    print("MEDORQIS FOUNDATION MODEL — QLORA CLOUD TRAINING PIPELINE")
    print(f"Base Model: {args.model_id}")
    print(f"Target LoRA Hub: {args.output_repo}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Device: {torch.cuda.get_device_name(0)} (VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB)")
    print("=" * 70)

    # 1. 4-Bit BitsAndBytes Configuration
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True
    )

    # 2. Tokenizer
    print("[1/5] Loading Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_id,
        token=HF_TOKEN,
        trust_remote_code=True,
        padding_side="right"
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 3. Base Model Quantized Load
    print(f"[2/5] Loading Base Model in 4-bit NF4: {args.model_id}...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        quantization_config=bnb_config,
        device_map="auto",
        token=HF_TOKEN,
        trust_remote_code=True,
        attn_implementation="flash_attention_2" if torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8 else "eager"
    )
    
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

    # 4. LoRA Target Configuration
    print("[3/5] Setting up PEFT LoRA Adapters...")
    peft_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # 5. Dataset Loading & Formatting
    print(f"[4/5] Loading Dataset from: {args.dataset_path}...")
    if args.dataset_path.endswith(".jsonl"):
        dataset = load_dataset("json", data_files=args.dataset_path, split="train")
    else:
        dataset = load_dataset(args.dataset_path, split="train", token=HF_TOKEN)

    formatted_dataset = dataset.map(lambda ex: format_chatml_prompt(ex, tokenizer))

    # 6. Training Arguments & SFTTrainer
    print("[5/5] Launching SFTTrainer...")
    output_dir = "./medorqis_lora_checkpoints"
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=args.num_train_epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        bf16=True,
        logging_steps=5,
        save_strategy="epoch",
        optim="paged_adamw_8bit",
        report_to="none"
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=formatted_dataset,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
        tokenizer=tokenizer,
        args=training_args,
        peft_config=peft_config
    )

    trainer.train()

    # 7. Save and Push LoRA Adapter directly to Hugging Face
    print(f"[COMPLETE] Training finished! Uploading LoRA adapter to Hugging Face: {args.output_repo}...")
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    if args.output_repo:
        try:
            trainer.model.push_to_hub(args.output_repo, token=HF_TOKEN)
            tokenizer.push_to_hub(args.output_repo, token=HF_TOKEN)
            print(f"[SUCCESS] LoRA Adapter published live to https://huggingface.co/{args.output_repo}")
        except Exception as e:
            print(f"[WARNING] Push to Hub encountered an error: {e}. Checkpoints are saved locally at {output_dir}")


if __name__ == "__main__":
    main()
