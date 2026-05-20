"""
================================================================
 CSP Solver -- Kaggle GPU Inference Server
 ------------------------------------------
 Copy-paste this ENTIRE file into a single Kaggle notebook cell
 and run it.

 Prerequisites:
   - Kaggle notebook with GPU accelerator enabled (T4)
   - Internet access enabled in notebook settings

 What it does:
   1. Installs dependencies
   2. Loads Qwen2.5-Coder-7B-Instruct in 4-bit quantization
   3. Starts a Flask API server
   4. Exposes it via ngrok so your local machine can call it
================================================================
"""

# ── Step 0: Install dependencies ─────────────────────────────
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])

install("flask")
install("pyngrok")
install("transformers>=4.42.0")
install("accelerate>=0.30.0")
install("bitsandbytes>=0.43.0")
install("torch")

# ── Step 1: Load the model ───────────────────────────────────
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

# Qwen2.5-Coder-7B-Instruct is UNGATED -- no HuggingFace token needed
MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"

print(f"Loading {MODEL_ID} in 4-bit quantization...")

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=quantization_config,
    device_map="auto",
    torch_dtype=torch.float16,
    trust_remote_code=True,
)

print(f"Model loaded successfully!")

# ── Step 2: Flask API ────────────────────────────────────────
from flask import Flask, request, jsonify
import json
import re
import threading

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ready",
        "model": MODEL_ID,
        "device": str(model.device),
        "quantization": "4-bit NF4",
    })


@app.route("/generate", methods=["POST"])
def generate():
    """Generate text from chat messages.

    Request body:
    {
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
        ],
        "temperature": 0.1,
        "max_tokens": 4096,
        "json_mode": false
    }
    """
    try:
        data = request.json
        messages = data.get("messages", [])
        temperature = data.get("temperature", 0.1)
        max_tokens = data.get("max_tokens", 4096)
        json_mode = data.get("json_mode", False)

        if not messages:
            return jsonify({"error": "No messages provided"}), 400

        # If json_mode, append instruction to the last user message
        if json_mode:
            suffix = (
                "\n\nIMPORTANT: You MUST respond with ONLY valid JSON. "
                "No markdown, no code fences, no explanation outside the JSON. "
                "Start your response with { and end with }."
            )
            for i in range(len(messages) - 1, -1, -1):
                if messages[i].get("role") == "user":
                    messages[i]["content"] += suffix
                    break

        # Use the tokenizer's built-in chat template (works for Qwen)
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        input_length = inputs["input_ids"].shape[1]

        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=max(temperature, 0.01),
                do_sample=temperature > 0.01,
                top_p=0.95,
                repetition_penalty=1.1,
            )

        # Decode only the new tokens
        generated_tokens = outputs[0][input_length:]
        content = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

        # If json_mode, try to extract JSON from the response
        if json_mode:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

        return jsonify({
            "content": content,
            "model": MODEL_ID,
            "tokens_generated": len(generated_tokens),
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ── Step 3: ngrok tunnel ─────────────────────────────────────
from pyngrok import ngrok

NGROK_TOKEN = "3CR6NAu7YFXG9SfobEpW3fmKj5V_2C8TTX6npCUQHBBLVoXa8"

ngrok.set_auth_token(NGROK_TOKEN)

public_url = ngrok.connect(5000)
print("=" * 60)
print("KAGGLE INFERENCE SERVER READY")
print("=" * 60)
print(f"  Public URL: {public_url}")
print(f"  Health:     {public_url}/health")
print(f"  Generate:   {public_url}/generate")
print("=" * 60)
print()
print("Copy this URL into your .env file:")
print(f"   KAGGLE_INFERENCE_URL={public_url}")
print("=" * 60)

# ── Step 4: Run the server ───────────────────────────────────
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5001)).start()

print("\nServer is running. Keep this notebook tab open.")
print("The server will stay alive as long as the Kaggle session is active (~12 hours).")
