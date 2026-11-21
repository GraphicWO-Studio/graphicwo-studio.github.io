# GraphicWO AI — weekly LoRA training (runs on Kaggle's free GPU).
# Base model: FLUX.2 [klein] 4B Base (Apache-2.0). Output: /kaggle/working/out/pytorch_lora_weights.safetensors
import glob, json, os, shutil, subprocess, sys

def sh(cmd):
    print("+", cmd, flush=True)
    subprocess.run(cmd, shell=True, check=True)

DATA = next(iter(glob.glob("/kaggle/input/*/metadata.jsonl") + glob.glob("/kaggle/input/**/metadata.jsonl", recursive=True)), None)
if not DATA:
    sys.exit("No training data found")
DATA_DIR = os.path.dirname(DATA)
WORK, OUT = "/kaggle/temp/data", "/kaggle/working/out"
shutil.copytree(DATA_DIR, WORK, dirs_exist_ok=True)
n = sum(1 for _ in open(DATA, encoding="utf-8"))
print("training images:", n)

sh("pip install -q -U git+https://github.com/huggingface/diffusers.git peft accelerate transformers bitsandbytes datasets sentencepiece")
sh("wget -q -O train.py https://raw.githubusercontent.com/huggingface/diffusers/main/examples/dreambooth/train_dreambooth_lora_flux2_klein.py")
json.dump({"load_in_4bit": True, "bnb_4bit_quant_type": "nf4", "bnb_4bit_compute_dtype": "float16"}, open("bnb.json", "w"))

import torch
bf16 = torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8
steps = max(300, min(1500, n * 10))
sh(" ".join([
    "accelerate launch --num_processes 1 train.py",
    "--pretrained_model_name_or_path=black-forest-labs/FLUX.2-klein-base-4B",
    f"--instance_data_dir={WORK}", "--caption_column=prompt", "--instance_prompt='graphicwo style'",
    f"--output_dir={OUT}", "--bnb_quantization_config_path=bnb.json",
    "--gradient_checkpointing", "--cache_latents", "--offload",
    "--resolution=512", "--train_batch_size=1", "--gradient_accumulation_steps=4",
    "--guidance_scale=1", "--use_8bit_adam", "--optimizer=adamW", "--learning_rate=1e-4",
    "--lr_scheduler=constant", "--lr_warmup_steps=50", f"--max_train_steps={steps}",
    "--rank=16", "--lora_alpha=16", "--checkpointing_steps=100000", "--skip_final_inference",
    f"--mixed_precision={'bf16' if bf16 else 'fp16'}", "--seed=0", "--report_to=tensorboard",
]))
json.dump({"images": n, "steps": steps, "base": "black-forest-labs/FLUX.2-klein-base-4B"}, open(f"{OUT}/train_info.json", "w"))
for p in glob.glob(f"{OUT}/checkpoint-*"):
    shutil.rmtree(p, ignore_errors=True)
print("done:", os.listdir(OUT))
