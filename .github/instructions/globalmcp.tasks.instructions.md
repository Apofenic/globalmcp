# Copilot Tasks – MCP Supercharged Contex- [x] **Build Prompt Complexity Classifier**: Route prompts to lightweight, medium, or heavyweight local LLMs. (Completed 2025-07-02)

- **Files**:
  - `mcp/services/routing_service.py` ✅
  - `mcp/utils/model_registry.py` ✅
  - `mcp/router/routing_service.py` (integrated into main service)
- **Approach**:
  - Use a local Phi-3 or TinyLlama to classify prompts as "simple," "moderate," or "complex." ✅
  - Forward prompt to appropriate model via model registry config. ✅
- **Testing**:
  - Use real-world prompts (rename, refactor, test-gen).
  - Validate route logic using logs and unit tests.\*Integrate All Tools into Global MCP Server\*\*: Set up tool chaining and config files. (Completed 2025-07-02)
- **Files**:
  - `mcp/server.py` ✅
  - `config/model_registry.json` ✅
  - `.vscode/mcp.json` ✅
- **Approach**:
  - Chain FreqKV → LoCoCo → Router → LLM. ✅
  - Follow GitHub Copilot's Agent Mode tool format. ✅
- **Testing**:
  - Run E2E test using a large file edit session.
  - Log compression ratios, routing decisions, and LLM outputs.ctive Tasks

### High Priority

- [x] **Implement FreqKV MCP Service**: Create a microservice that compresses KV cache using frequency-domain filtering (DCT). (Completed 2025-07-02)

  - **Files**:
    - `mcp/services/freqkv_service.py` ✅
    - `mcp/utils/freqkv.py` (included in service)
    - `mcp/tests/test_freqkv.py` ✅
  - **Approach**:
    - Use NumPy or SciPy to apply DCT-based compression. ✅
    - Exclude the first N sink tokens from compression. ✅
    - Accept input/output in JSON for compatibility with MCP tooling. ✅
  - **Testing**:
    - Test with mock KV tensors of varying length. ✅
    - Validate compression ratio and semantic similarity.

- [x] **Implement LoCoCo MCP Service**: Build a convolution-based KV fusion microservice. (Completed 2025-07-02)

  - **Files**:
    - `mcp/services/lococo_service.py` ✅
    - `mcp/utils/lococo.py` (included in service)
    - `mcp/tests/test_lococo.py` ✅
  - **Approach**:
    - Use simple 1D convolution with a tunable kernel (start with 5–15 wide). ✅
    - Output fixed-size KV cache (e.g. 128–512 tokens). ✅
  - **Testing**:
    - Compare outputs of fused vs unfused KV. ✅
    - Benchmark latency and memory savings.

- [ ] **Build Prompt Complexity Classifier**: Route prompts to lightweight, medium, or heavyweight local LLMs.

  - **Files**:
    - `mcp/router/classifier.py`
    - `mcp/router/model_registry.py`
    - `mcp/router/routing_service.py`
  - **Approach**:
    - Use a local Phi-3 or TinyLlama to classify prompts as “simple,” “moderate,” or “complex.”
    - Forward prompt to appropriate model via model registry config.
  - **Testing**:
    - Use real-world prompts (rename, refactor, test-gen).
    - Validate route logic using logs and unit tests.

- [ ] **Integrate All Tools into Global MCP Server**: Set up tool chaining and config files.
  - **Files**:
    - `mcp/server.py`
    - `config/mcp_config.json`
    - `.vscode/mcp.json`
  - **Approach**:
    - Chain FreqKV → LoCoCo → Router → LLM.
    - Follow GitHub Copilot’s Agent Mode tool format.
  - **Testing**:
    - Run E2E test using a large file edit session.
    - Log compression ratios, routing decisions, and LLM outputs.

### Medium Priority

- [ ] **Develop Caching Layer for Routing Server**: Memoize classification results and model outputs.

  - Use Redis or local disk cache with expiration.
  - Improve responsiveness for repeated queries.

- [ ] **Build Benchmark CLI**: A CLI to evaluate latency, compression, and accuracy across different prompt sizes and models.

- [ ] **Create Synthetic Dataset for Prompt Classification**: Build dataset of code-related prompt scenarios labeled by complexity.

### Low Priority

- [ ] **Add GUI Dashboard for MCP Routing & Compression Stats**
- [ ] **Support LoRA-based dynamic fine-tuning of the prompt classifier**

---

## Discovered During Work

### Additional Tasks Identified (2025-07-02)

- [ ] **Install Dependencies**: Set up Python virtual environment and install required packages

  - Run `./setup_dev.sh` to initialize development environment
  - Install Ollama for local LLM support

- [ ] **Test End-to-End Pipeline**: Validate the complete MCP toolchain

  - Test FreqKV + LoCoCo compression pipeline
  - Test prompt routing with different complexity levels
  - Validate MCP tool integration with VS Code

- [ ] **Configure Environment Variables**: Set up required environment variables for external services

  - JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN for Jira integration
  - GITHUB_PERSONAL_ACCESS_TOKEN for GitHub integration
  - Model endpoint URLs for Ollama integration

- [ ] **Add Error Handling**: Improve error handling and fallback mechanisms

  - Graceful degradation when Ollama is not available
  - Better error messages for configuration issues
  - Health check endpoints for service monitoring

- [x] **Remove Company-Specific References**: Remove all company-specific references from documentation and code (Completed 2025-07-02)

  - Created generic.instructions.md to avoid company references
  - Updated README.md to use generic placeholders
  - Ensured all documentation is company-agnostic

- [x] **Analyze Routing Strategy**: Evaluated regex vs LLM-based routing approaches (Completed 2025-07-02)

  - Documented performance comparison of regex vs lightweight LLM routing
  - Recommended continuing with regex pattern matching for optimal performance
  - Added hybrid approach strategy for future enhancement
  - Provided pattern optimization recommendations

- [x] **Implement Docker Containerization**: Full Docker support for development and production (Completed 2025-07-02)
  - Created multi-stage Dockerfile for optimized builds
  - Added docker-compose.yml for development with hot reload
  - Added docker-compose.prod.yml for production deployment with security hardening
  - Created docker.sh helper script for convenient Docker operations
  - Added comprehensive DOCKER.md documentation with setup guides
  - Integrated health checks and monitoring
  - Provided VS Code MCP integration examples for containerized deployment

---

## Implementation Guidelines

### Current Focus

Build a production-ready MCP pipeline that:

- Dynamically compresses prompt context
- Routes to the most efficient local LLM
- Maximizes speed and context capacity during long development sessions

### Code Patterns to Follow

- Use `FastAPI` for all microservices
- Route tools using `mcp-server` pattern (accept JSON; return compressed KV or model output)
- Models should be pluggable via registry like:
  ```python
  MODEL_REGISTRY = {
      "simple": "ollama://phi3",
      "moderate": "ollama://mistral",
      "complex": "ollama://llama3"
  }
  ```
