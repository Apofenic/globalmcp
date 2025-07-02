## applyTo: "\*\*"

# Copilot MCP Compression & Routing – Planning Instructions

## Project Overview

This project creates a modular, extensible toolchain using GitHub Copilot’s MCP (Model Customization Protocol) to:

- Compress large prompt contexts using frequency and convolutional techniques (FreqKV & LoCoCo).
- Dynamically route prompts to local LLMs (Tiny, Medium, or Large) based on prompt complexity.
- Extend the effective working context of Copilot during large, multi-file or long-lived coding sessions.

Goal: Enable faster, smarter, and longer coding interactions with Copilot using smart local tools.

---

## Architecture Overview

- **Technology Stack**:

  - Python 3.10+ (FastAPI for microservices)
  - NumPy / SciPy (for KV processing)
  - Ollama (for local LLM orchestration)
  - GitHub Copilot Agent Mode (MCP tool interface)
  - Redis (for optional routing/memory cache)

- **Design Patterns**:

  - Microservice Architecture
  - Mixture of Experts (MoE) Routing
  - MCP Toolchain Composition
  - Functional Service Isolation

- **Key Components**:
  - `freqkv_service`: Frequency-domain compressor for KV cache.
  - `lococo_service`: Convolution-based KV fuser for context retention.
  - `routing_service`: Classifies prompt complexity and forwards to appropriate model.
  - `model_registry`: Maps prompt types to LLM endpoints.
  - `copilot_agent_chain`: Chains all services together as part of Copilot Agent Mode.

---

## Current Focus Areas

- [x] **Phase 1**: Architecture research and prototype planning (completed).
- [ ] **Phase 2**: Build and test FreqKV, LoCoCo, and prompt routing services independently.
- [ ] **Phase 3**: Chain tools via MCP and integrate with GitHub Copilot Agent Mode.
- [ ] **Phase 4**: Add caching, test datasets, and benchmarking for local dev performance.

---

## Key Architectural Decisions

1. **Prompt Routing via Local Classifier**:  
   Use a lightweight LLM (e.g. Phi-3, TinyLlama) to classify prompt complexity and route accordingly. Avoids overloading larger models and cuts latency on simple tasks.

2. **KV Compression via DCT + Convolution**:  
   FreqKV handles semantic compression (drop high-frequency info), and LoCoCo handles spatial compression (fuse tokens into fewer slots). Combining both maintains prompt fidelity while shrinking size for model consumption.

3. **Model Agnosticism via Registry**:  
   All model endpoints are abstracted in a registry layer. This allows plug-and-play swapping of LLMs (Ollama, llama.cpp, vLLM) without changing routing logic.

---

## Integration Points

- **External APIs**:

  - GitHub Copilot MCP Toolchain (Agent Mode)
  - Optional: Claude Sonnet 4 / GPT-4 as fallback cloud inference endpoints

- **Internal Services**:

  - `freqkv_service`
  - `lococo_service`
  - `routing_service`
  - `model_proxy_service` (for LLMs via Ollama or similar)

- **Data Flow**:
  1. Editor → Copilot context buffer
  2. KV → FreqKV → LoCoCo
  3. Prompt → Router → LLM (via model registry)
  4. Output → Copilot response

---

## Security Considerations

- No external data leaves the dev machine (unless using optional cloud model fallback).
- LLM endpoints are run locally with isolated access.
- Tools can be run in a container sandbox (Docker or Firejail for extra isolation).
- No persistent user data logged unless explicitly opted-in for telemetry.

---

## Performance Requirements

- **Expected Load**:

  - Support for 5–20 file active contexts (~200K–2M tokens).
  - Up to 10 requests/minute per developer session.

- **Performance Targets**:

  - Compression + Routing latency ≤ 250ms
  - Total toolchain response time (incl. LLM) ≤ 2s

- **Optimization Priorities**:
  - Prefer routing simple prompts to 1.5B–3B models to reduce GPU usage.
  - Cache model outputs and classifier results.
  - Optimize FreqKV and LoCoCo for array throughput (batching, GPU optional).
