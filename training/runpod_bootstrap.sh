#!/usr/bin/env bash
# MedOrqis Foundation Model — Cloud GPU Bootstrap Script
# Runs inside the RunPod / Cloud GPU environment (Not on local PC)
set -e

echo "=========================================================="
echo "MEDORQIS FOUNDATION MODEL — CLOUD POD BOOTSTRAP INITIALIZING"
echo "=========================================================="
nvidia-smi

# 1. Install high-performance dependencies in cloud container
pip install --upgrade pip
pip install -q \
    transformers==4.47.0 \
    datasets \
    accelerate \
    bitsandbytes>=0.44.0 \
    peft>=0.14.0 \
    trl>=0.12.0 \
    huggingface_hub \
    sentencepiece \
    tiktoken

echo "[1/3] Environment prepared."

# 2. Build training dataset
python3 training/dataset_builder.py
echo "[2/3] Dataset generated in cloud."

# 3. Launch QLoRA Fine-tuning
echo "[3/3] Launching QLoRA Training on Karnak Foundation Model..."
python3 training/train_qlora.py \
    --model_id "Applied-Innovation-Center/Karnak-40B-v1.0" \
    --output_repo "seotarek/medorqis-karnak-40b-lora" \
    --num_train_epochs 3 \
    --batch_size 2 \
    --gradient_accumulation_steps 8 \
    --learning_rate 2e-4

echo "=========================================================="
echo "TRAINING AND HF UPLOAD COMPLETED SUCCESSFULLY!"
echo "=========================================================="
