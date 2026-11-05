#!/usr/bin/env python3
"""
Sets up the official Hugging Face Model Repository and uploads
the complete, professional Model Card (README.md) for MedOrqis-Hakim-6B.
"""

import os
import sys
from huggingface_hub import HfApi, create_repo

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
if not HF_TOKEN:
    print("[ERROR] HF_TOKEN is not set.")
    sys.exit(1)

REPO_ID = "seotarek/medorqis-hakim-6b"

MODEL_CARD_CONTENT = """---
language:
- ar
- en
license: apache-2.0
base_model: Applied-Innovation-Center/Karnak-6B-v1.0
tags:
- medical
- clinical-reasoning
- arabic-medical
- tool-calling
- function-calling
- qwen3
- cardiology
- nephrology
- pharmacology
- pediatrics
- safety-guardrails
pipeline_tag: text-generation
library_name: peft
datasets:
- seotarek/medorqis-clinical-instructions
- seotarek/medorqis-clinical-dialect-benchmark
model-index:
- name: MedOrqis-Hakim-6B
  results: []
---

<div align="center">

# 🩺 MedOrqis-Hakim-6B (حكيم)
### Bilingual Medical Foundation Model & Deterministic Clinical Tool-Calling Brain
#### النموذج الطبي الذكي ثنائي اللغة الموجه بالمعايير السريرية العالمية والحسابات الحتمية

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Base Model](https://img.shields.io/badge/Base_Model-Karnak--6B--v1.0-emerald.svg)](https://huggingface.co/Applied-Innovation-Center/Karnak-6B-v1.0)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/seotarek/MedOrqis/blob/main/training/MedOrqis_Free_Training_Colab.ipynb)
[![Dataset](https://img.shields.io/badge/Dataset-MedOrqis--Clinical--Instructions-orange.svg)](https://huggingface.co/datasets/seotarek/medorqis-clinical-instructions)
[![M8ven Verified](https://img.shields.io/badge/M8ven_Trust-Grade_B_(89%2F100)-green.svg)](https://m8ven.ai/mcp/seotarek-medorqis-uxezzz?s=readme)

</div>

---

## 📌 1. نبذة عن النموذج (Model Overview)

**MedOrqis-Hakim-6B (حكيم)** هو نموذج لغوي طبي سريري متخصص ثنائي اللغة (العربية والإنجليزية)، تم تطويره كنواة عصبية ذكية (Clinical Brain) مكملة لمنظومة مهارات **MedOrqis**. النموذج مبني فوق الأساس الطبي العربي **Karnak-6B-v1.0** (من معمارية Qwen3) ومدرب بتقنية **QLoRA** على مجموعات بيانات سريرية واقعية.

### 💡 لماذا سُمي "حكيم" (Hakim)؟
في التراث الطبي العربي، "الحكيم" ليس مجرد ناقل للمعرفة، بل هو الطبيب الفيلسوف الذي يجمع بين عمق الفحص السريري، وحسن الاستماع للمريض، والالتزام بأعلى معايير الأمانة والسلامة السريرية.

---

## 🏛️ 2. الهيكلية ثنائية المسار (The Dual-Track Architecture)

يعتمد **MedOrqis** على فصل جوهري صارم بين مسارين لمنع الهلوسة الطبية:

```mermaid
graph TD
    User["المريض / الطبيب (Clinical Narrative / Complaint)"] --> Brain["المسار الأول: MedOrqis-Hakim Brain<br/>(Clinical Reasoning & Syntactic Understanding)"]
    Brain --> Decision{"هل تحتاج الحالة<br/>لحسابات أو قواعد أمان؟"}
    Decision -- "نعم (Math/Risk/Dosing/DDI)" --> ToolCall["استدعاء تلقائي للأداة الحتمية<br/>&lt;tool_call&gt;"]
    ToolCall --> MCP["المسار الثاني: محرك مهارات MedOrqis<br/>(Deterministic MCP Calculators & Guardrails)"]
    MCP --> Result["ناتج حسابي دقيق 100% بدون هلوسة"]
    Result --> Synthesis["صياغة التوصية الطبية السريرية المعتمدة<br/>(ESC 2024 / KDIGO / NICE)"]
    Decision -- "لا (تحليل سردي فقط)" --> Direct["تحليل سريري موجه"]
    Synthesis --> Output["التقرير الطبي النهائي الموثق"]
    Direct --> Output
```

1. **المسار الأول (The Brain)**: نموذج **MedOrqis-Hakim** الذي يفهم الشكوى السريرية، ويترجم اللهجات العامية (مثل: المصرية والخليجية) إلى تشخيصات معيارية (ICD-10 / SNOMED-CT).
2. **المسار الثاني (The Deterministic Engine)**: محرك أدوات MedOrqis الذي ينفذ العمليات الحسابية وقواعد الأمان الحرجة عبر **معادلات برمجية حتمية (Zero-Token Deterministic Equations)** خالية تماماً من الهلوسة الاحتمالية.

---

## 🧮 3. الأدوات والحاسبات السريرية الحتمية المدعومة (Deterministic Tools)

تم تدريب النموذج على توليد استدعاءات برمجية مباشرة عبر وسوم ChatML `<tool_call>` للأدوات التالية:

| اسم الأداة الحسابية | المرجع العلمي المعتمد | الوظيفة السريرية |
| :--- | :--- | :--- |
| **`cha2ds2_va_esc2024`** | ESC 2024 AF Guidelines | تقييم خطورة الجلطات لمرضى الرجفان الأذيني (بعد استبعاد عامل الجنس البيولوجي). |
| **`ckd_epi_2021_egfr`** | KDIGO 2024 / NKF-ASN | حساب معدل الترشيح الكبيبي الكلوي بالمعادلة المعتمدة الخالية من العرق. |
| **`bedside_schwartz_egfr`** | KDIGO Pediatric | حساب كفاءة وظائف الكلى للأطفال دون سن 18 عاماً. |
| **`cockcroft_gault_crcl`** | FDA Renal Dosing | حساب تصفية الكرياتينين لتعديل جرعات الأدوية كلوياً. |
| **`curb65_score`** | BTS Guidelines | تقييم شدة الالتهاب الرئوي وتحديد معايير القبول بالعناية المركزة. |
| **`wells_pe_score`** | Wells Criteria | تحديد احتمالية الإصابة بالانصمام الرئوي (PE) وتوجيه الفحوصات الإشعاعية. |
| **`has_bled_score`** | Chest Guidelines | تقييم خطورة النزيف لمرضى مضادات التخثر. |
| **`pediatric_weight_dose`** | AAP Guidelines | حساب جرعات الأطفال الدوائية حسب الوزن بدقة مع سقف جرعة البالغين (Zero Overdose). |
| **`check_drug_interactions`** | MedOrqis DDI Engine | رصد التداخلات الدوائية القاتلة والتعارضات بين الأدوية. |
| **`check_red_flags`** | Emergency Protocols | التقاط العلامات الحمراء الحادة (مثل: متلازمة ذنب الفرس، الصدمة، الذبحة الصدرية). |
| **`scrub_phi`** | HIPAA Safe Harbor | التطهير الآلي لبيانات المرضى الشخصية والأرقام القومية والهواتف. |

---

## 💬 4. أمثلة الاستخدام وتوليد استدعاء الأدوات (Prompt & Tool-Calling)

### سيناريو سريري باللغة العربية (Cardiology Case):

```json
{
  "role": "user",
  "content": "مريض عمره 68 سنة يعاني من رجفان أذيني غير صمام، ولديه ارتفاع ضغط دم وتصلب شرايين محيطية. كيف نقيم خطورة الجلطات وفق ESC 2024؟"
}
```

### استجابة النموذج (MedOrqis-Hakim Model Output):

```xml
<tool_call>
{"name": "calculate_clinical_score", "arguments": {"calculator_id": "cha2ds2_va_esc2024", "parameters": {"age_years": 68, "hx_hypertension": true, "hx_diabetes": false, "hx_stroke_tia_thromboembolism": false, "hx_vascular_disease": true, "hx_heart_failure": false}}}
</tool_call>
```

---

## 🚀 5. كيفية تشغيل واستخدام النموذج برمجياً (Quickstart with Python)

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_model_id = "Applied-Innovation-Center/Karnak-6B-v1.0"
lora_model_id = "seotarek/medorqis-hakim-6b"

# 1. تحميل الـ Tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model_id, trust_remote_code=True)

# 2. تحميل النموذج الأساسي بضغط 4-bit
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    load_in_4bit=True,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True
)

# 3. دمج محولات الحكيم (Hakim LoRA Adapters)
model = PeftModel.from_pretrained(base_model, lora_model_id)
model.eval()

# 4. استعلام سريري
prompt = "Patient with acute retrosternal chest pain and diaphoresis. Analyze symptoms."
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.2)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

---

## 📊 6. بيانات التدريب والتقييم (Datasets & Benchmarks)

- **بيانات التعليمات السريرية**: [`seotarek/medorqis-clinical-instructions`](https://huggingface.co/datasets/seotarek/medorqis-clinical-instructions)
- **بيانات معالجة اللهجات الإقليمية**: [`seotarek/medorqis-clinical-dialect-benchmark`](https://huggingface.co/datasets/seotarek/medorqis-clinical-dialect-benchmark)

---

## 🛡️ 7. إخلاء المسؤولية الطبية والأمان (Clinical Safety Disclaimer)

> **تنبيه سريري هام**: نموذج **MedOrqis-Hakim** صُمم كنظام دعم قرار سريري تجريبي (Clinical Decision Support - CDS) لمساعدة الكوادر الطبية والباحثين. هذا النموذج لا يحل بأي حال من الأحوال محل الفحص الطبي المباشر بواسطة طبيب بشري مرخص ومؤهل. لا تتخذ أي قرار علاجي أو دوائي بناءً على مخرجات الذكاء الاصطناعي دون استشارة طبية متخصصة.

---

## 📜 8. التوثيق والاقتباس (Citation)

```bibtex
@misc{medorqis_hakim_2026,
  author = {Tarek, SEO and The MedOrqis Engineering Team},
  title = {MedOrqis-Hakim-6B: Bilingual Medical Foundation Model & Deterministic Tool-Calling Brain},
  year = {2026},
  publisher = {Hugging Face},
  howpublished = {\\url{https://huggingface.co/seotarek/medorqis-hakim-6b}}
}
```
"""

def setup_repo():
    api = HfApi(token=HF_TOKEN)
    print("=" * 65)
    print(f"CREATING & CONFIGURING HUGGING FACE MODEL: {REPO_ID}")
    print("=" * 65)

    try:
        create_repo(repo_id=REPO_ID, repo_type="model", private=False, token=HF_TOKEN, exist_ok=True)
        print(f"[SUCCESS] Model repo created/verified: https://huggingface.co/{REPO_ID}")
    except Exception as e:
        print(f"[NOTE] create_repo: {e}")

    # Write Model Card
    card_path = "training/MODEL_CARD_HAKIM_6B.md"
    with open(card_path, "w", encoding="utf-8") as f:
        f.write(MODEL_CARD_CONTENT)

    api.upload_file(
        path_or_fileobj=card_path,
        path_in_repo="README.md",
        repo_id=REPO_ID,
        repo_type="model",
        token=HF_TOKEN
    )
    print(f"[SUCCESS] Model Card (README.md) published live to: https://huggingface.co/{REPO_ID}")
    print("=" * 65)

if __name__ == "__main__":
    setup_repo()
