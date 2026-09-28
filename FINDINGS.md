# Empirical Investigation & Finding: OpenRouter `typesafe/jev-router` Routing Behavior

**Date:** 2026-09-28  
**Endpoint Tested:** `typesafe/jev-router` (via OpenRouter API)  
**SDK Used:** `openrouter-1.2.32`

---

## 1. Executive Summary

When testing the verbatim boilerplate from OpenRouter against the `typesafe/jev-router` endpoint, two critical findings were uncovered:

1. **Multimodal Payload Handling:**
   - The verbatim boilerplate with multimodal inputs (`input_audio`, `image_url`, `video_url`) triggered an upstream gateway payment check:
     `PaymentRequiredResponseError: This request requires at least $0.50 in balance for audio`.
2. **Text Prompt Routing & Underlying Model Identity:**
   - When stripped of audio and video to send a standard user prompt (`"Which model are you?"`), the endpoint succeeded.
   - **Crucial Finding:** The endpoint does **not** behave as an isolated, non-generative "System-1" decision classifier. Instead, it acts as a router/proxy delegating generative conversational chat to **OpenAI models**.
   - In successive queries, the model self-identified as:
     - Trial 1: `"I’m ChatGPT, powered by OpenAI’s GPT-5.2."`
     - Trial 2: `"I’m ChatGPT, powered by OpenAI’s GPT-5.4 model."`
   - Inspection of OpenRouter's raw response metadata revealed that the underlying routed model was:
     `model='openai/gpt-6-luna'`.

---

## 2. Empirical Evidence & Trace Logs

### Test Run 1: Verbatim Multimodal Payload
```python
response = client.chat.send(
    model="typesafe/jev-router",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What is in this audio, image and video?"},
            {"type": "input_audio", "input_audio": {"data": "...", "format": "wav"}},
            {"type": "image_url", "image_url": {"url": "https://..."}},
            {"type": "video_url", "video_url": {"url": "https://..."}},
        ]
    }]
)
```
**Result:**
```text
Exception Type: PaymentRequiredResponseError
Error Message: This request requires at least $0.50 in balance for audio
```

---

### Test Run 2: Conversational Prompt (`"Which model are you?"`)
```python
response = client.chat.send(
    model="typesafe/jev-router",
    messages=[{"role": "user", "content": "Which model are you?"}]
)
```

**Captured Raw API Response Metadata:**
```yaml
Timestamp: 2026-09-28T13:03:48.507328+00:00
Requested Model: typesafe/jev-router
Underlying Routed Model: openai/gpt-6-luna
Generation ID: gen-1790600626-mIVbJpCDXKYoVfrIJllb
Assistant Output: "I’m ChatGPT, powered by OpenAI’s GPT-5.4 model."
Usage Details:
  prompt_tokens: 11
  completion_tokens: 21
  total_tokens: 32
  cost: $0.0000116
```

---

## 3. Analysis & Implications

1. **Jev as a "System-One" Classifier vs. Generative LLM:**
   - In benchmark suites and academic definitions (e.g., TypeSafe AI's System-One specs), Jev is conceptualized as an ultra-fast, structured decision model rather than an open-ended conversational agent.
   - However, on OpenRouter, `typesafe/jev-router` functions as a router or wrapper. When presented with standard unstructured text queries, it routes the payload to upstream OpenAI models (`openai/gpt-6-luna`).

2. **Why the Model "Talks":**
   - Because the endpoint routed to an OpenAI GPT model, the assistant responded in standard ChatGPT persona.
   - The router metadata confirms `openai/gpt-6-luna` was invoked to fulfill the generation.

3. **Reproduction Script:**
   - The test script can be reproduced at any time via:
     ```powershell
     cd openrouter_jev_dev
     .\.venv\Scripts\python.exe record_finding.py
     ```
