# Day 4 – Will It Fit, and May I Use It?

## Scenario

**Machine:** Windows 11, 15.2 GB RAM, 6 GB GPU VRAM  
**Purpose:** Run an open LLM locally as a coding/AI-agent assistant  
**Memory Budget:** 5.4 GB

## 3.1 Explanation of Concepts

### Model Weights
Model weights are the learned values of an LLM. More parameters generally require more memory.

### Quantization
Quantization reduces the memory required for model weights by using fewer bits.

Example: Q3 < Q4 < Q5 < Q6 < Q8 < FP16 in memory usage.

### KV Cache and Context Length
KV cache stores information from previous tokens. Increasing context length increases KV cache memory.

**Key point:** Weights stay the same, but KV cache increases with context.

### Model Card
A model card provides information about the model, such as parameters, context length, licence, and capabilities.

### Open-Weight vs Open-Source Licensing
A model can have publicly available weights but still have specific licence conditions. The exact licence must be checked before use.

## 3.2 Memory Estimate and Model Comparison

### Memory Estimate Table

| Model | Quantization | Context | Weights | KV | Total | Fits? |
|---|---|---:|---:|---:|---:|---|
| Qwen 1.5B | Q4 | 8K | 0.85 GB | 0.24 GB | 1.20 GB | Yes |
| Qwen 8B | Q4 | 8K | 4.56 GB | 1.28 GB | 6.42 GB | No |
| Qwen 8B | Q5 | 8K | 5.44 GB | 1.28 GB | 7.39 GB | No |
| Qwen 8B | Q8 | 8K | 8.00 GB | 1.28 GB | 10.21 GB | No |
| Qwen 8B | FP16 | 8K | 16.00 GB | 1.28 GB | 19.01 GB | No |

### Ollama Models

| Model | `ollama list` Size |
|---|---:|
| qwen3:4b | 2.5 GB |
| qwen3:8b | 5.2 GB |
| qwen2.5:1.5b | 986 MB |

## 3.3 Context Length and Quantization Observation

### Context Length

For the 8B Q4 model:

| Context | KV Cache | Total |
|---:|---:|---:|
| 2K | 0.32 GB | 5.37 GB |
| 4K | 0.64 GB | 5.72 GB |
| 8K | 1.28 GB | 6.42 GB |
| 16K | 2.56 GB | 7.83 GB |

**Observation:** As context increases, KV cache increases while weights remain the same.

### Quantization

For the 8B model at 8K:

| Quantization | Weights | KV |
|---|---:|---:|
| Q3_K_M | 3.44 GB | 1.28 GB |
| Q4_K_M | 4.56 GB | 1.28 GB |
| Q5_K_M | 5.44 GB | 1.28 GB |
| Q8_0 | 8.00 GB | 1.28 GB |
| FP16 | 16.00 GB | 1.28 GB |

**Observation:** Quantization changes weight memory, while KV cache remains approximately the same.

## 3.4 Estimate Versus Reality

The estimator predicted:

```text
8B Q4, 8K
Weights: 4.56 GB
KV:      1.28 GB
Total:   6.42 GB
Budget:  5.4 GB

Actual Ollama result for qwen3:8b:

Size:      6.0 GB
Processor: 30% CPU / 70% GPU
Context:   4096

The 8B model did not fit completely in GPU memory, so Ollama used both CPU and GPU.

Other observed results:

qwen3:4b       → 3.2 GB, 100% GPU
qwen2.5:1.5b   → 1.2 GB, 100% GPU


3.5 Suitability Analysis

The 1.5B and 4B models ran completely on the GPU.

The 8B model required CPU/GPU split because its memory requirement exceeded the available GPU budget.

Therefore, model size, quantization, and context length must all be considered when running an LLM locally.

3.6 Conclusion

This experiment showed:

Larger models require more memory.
Quantization reduces weight memory.
Increasing context increases KV-cache memory.
The estimator gives an approximate memory requirement.
Actual Ollama usage can differ from the estimate.
The 8B model used CPU/GPU split on this machine, while the smaller models ran fully on the GPU.