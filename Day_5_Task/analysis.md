Day 5 — Serving Models Your Way

1. Scenario

This task uses a Student Expense and Budget Assistant. The assistant helps a student understand locally stored expense and budget information. Its default behaviour is to give short, clear answers, avoid guessing missing financial information, and use the available data when answering questions.

The scenario is suitable for local serving because it is small, private, and mainly used by one student.

2. Explanation of Concepts

What is Ollama?

Ollama is a local system for running and serving open language models. Its three main parts are the Ollama CLI, Ollama server, and model files.

The CLI is used to manage models and send requests, for example with ollama list, ollama show, ollama run, and ollama ps. The server runs locally and receives requests from the CLI, REST API, or OpenAI-compatible API. The model files contain the model data and configuration needed for inference.

For this scenario, the flow is:

Python program → Ollama server → custom expense-assistant model → model generates tokens → response returned to Python.

The model is loaded into memory when required. After the model processes the prompt, the generated response is returned to the requesting program.

What is a Modelfile?

A Modelfile packages default behaviour and parameters on top of an existing model.

For the expense assistant, the Modelfile uses:

FROM — selects the base model.

PARAMETER temperature — controls how deterministic the answers are.

PARAMETER num_ctx — controls the context window available to the model.

SYSTEM — defines the default behaviour of the expense assistant.

A low temperature is suitable because expense and budget questions should have consistent answers. The context size is selected according to available memory.

The custom model is based on the existing base model with additional configuration and system instructions. Therefore, creating the custom model does not download another full copy of the model weights.

Which system prompt wins?

If the program sends its own system prompt when using the custom model, the program-supplied system prompt overrides the Modelfile's default system behaviour.

This is useful when building an agent because the Modelfile provides a safe default, while the program can provide task-specific instructions when required.

/api/generate vs /api/chat

/api/generate is used for a direct prompt and generated response.

/api/chat is designed around chat messages such as system, user, and assistant messages. It is more suitable when the application needs conversation-style interaction.

Ollama also provides an OpenAI-compatible endpoint, such as /v1/chat/completions. This matters because applications written using an OpenAI-style client can use Ollama with the server address and model configuration changed. The same application structure can therefore be moved later to another compatible serving system such as vLLM.

Streaming, TTFT and total time

Streaming means the server sends generated output progressively instead of waiting for the complete answer.

TTFT (Time To First Token) measures how long it takes before the first generated token is received.

Total time measures the time from sending the request until the complete response is received.

Streaming makes the answer feel faster because the user starts seeing output after TTFT. It does not necessarily reduce the total generation time.

num_ctx, OLLAMA_KEEP_ALIVE and OLLAMA_NUM_PARALLEL

num_ctx controls how much context the model can process. A larger context requires more KV-cache memory.

OLLAMA_KEEP_ALIVE controls how long a loaded model remains in memory after a request. Keeping a model loaded can reduce the loading delay for the next request.

OLLAMA_NUM_PARALLEL controls how many requests can be processed in parallel by a model.

The connection between num_ctx and KV-cache memory is important: increasing the context length increases the amount of KV-cache memory required. Therefore, a larger context can increase memory usage even when the model weights do not change.

KV-cache, PagedAttention and prefix caching

During generation, the model stores key-value information in the KV cache. A simple allocation method can reserve a large continuous memory area for each request. When the actual request uses less space than reserved, part of the allocated memory is wasted.

PagedAttention divides KV-cache memory into fixed-size blocks and uses a block table to map the logical sequence to those blocks. This allows memory to be allocated more flexibly and reduces wasted memory.

Prefix caching provides another benefit. If several requests use the same beginning, such as the same system prompt for the expense assistant, the already-computed prefix can be reused instead of being recomputed.

This is especially useful for agents because an agent may repeatedly send the same system instructions and tool-related context.

Static batching vs continuous batching

In static batching, requests are grouped together and processed as a fixed batch. A request that finishes early may leave unused capacity while the remaining requests continue.

In continuous batching, new requests can be added as other requests finish. This keeps the available compute resources better utilised when many users are sending requests.

Throughput is the amount of work or tokens processed over a period of time.

TTFT is the time until the first token is produced.

TPOT (Time Per Output Token) measures the time taken per generated output token after generation starts.

P95 latency is the latency below which 95% of requests complete.

Increasing throughput can increase individual request latency because more requests share the available resources. Therefore, serving systems must balance throughput, TTFT, TPOT and P95 latency according to application requirements.

3. Ollama vs vLLM

Basis for comparison

Ollama

vLLM

Built for (who and how many users)

Local users and small applications

Shared production serving and many concurrent users

Hardware it needs

Can run on a normal personal computer with suitable CPU/GPU/RAM

Usually benefits from a capable NVIDIA GPU and sufficient VRAM

How it handles several requests at once

Simple local serving and configurable parallel requests

Designed for high-concurrency serving with continuous batching

How it manages memory

Local model loading and KV-cache management

Optimised serving with PagedAttention and efficient KV-cache management

Setup effort and model format

Simple setup and easy model management with Ollama models and Modelfiles

More production-oriented setup and deployment configuration

Your choice if only you use the scenario, and why

Ollama — simple, local, private and sufficient for one student

vLLM would be unnecessary for this use case

Your choice if 100 people use it at once, and why

Not my first choice because concurrent requests increase memory and scheduling pressure

vLLM — designed for efficient concurrent serving and better GPU utilisation

4. Minimal Implementation

The custom model is based on an existing Ollama model. The Modelfile contains one FROM instruction, at least two parameters, and a scenario-specific SYSTEM prompt.

Example configuration:

FROM qwen3:8b

PARAMETER temperature 0.2
PARAMETER num_ctx 4096
PARAMETER repeat_penalty 1.1

SYSTEM """
You are a Student Expense and Budget Assistant.
Answer expense and budget questions clearly and briefly.
Use only the information provided by the user or application.
Never invent missing expense or budget values.
If required information is missing, clearly say that it is missing.
"""

The Python implementation calls the Ollama REST API directly using requests. It uses a non-streaming request to measure total generation time and tokens per second. It also uses a streaming request to measure TTFT and total streaming time.

The OpenAI-compatible endpoint is used with the custom model and a different program-supplied system prompt. This demonstrates that the application can override the Modelfile's default behaviour.

| Run | Prompt                                     | Behaviour           | Tokens/s |   TTFT   |   Total   | Loaded        |           Observation               |
|     |                                            | followed?           |          |          |   Time    | before run?   |                                     |
| --- | ------------------------------------------ | ------------------- | -------: | -------: | --------: | ------------- | ----------------------------------- |
|   1 | How much did I spend on food?              | Yes                 |    10.07 |  17.50 s |   19.99 s | No            | First run may include model loading |
|   2 | Give me a simple budget tip for a student. | Yes                 |     9.85 |  37.52 s |   39.55 s | Yes           | Model should already be in memory   |
|   3 | Should I reduce my entertainment spending? | Yes                 |     9.94 |  21.38 s |   29.13 s | Yes           | Tests response and timing           |



Demonstrates system-prompt override

The first run can take longer because the model may need to be loaded into memory. A later run can be faster when the model remains loaded. This can be checked with ollama ps or /api/ps.

For the streaming request, TTFT represents the initial waiting time before output appears, while total time includes the complete response generation. Therefore, the user can see the beginning of the answer much earlier than the final completion time.

The main performance observation is that speed depends on the model and hardware. A smaller model normally requires less memory and can respond faster, while a larger model can require more memory and may take longer.

6. Suitability and Conclusion

For the student expense and budget assistant, Ollama on a single machine is sufficient because the scenario is small, private and intended for individual use. It provides simple model management, custom behaviour through a Modelfile, and direct access through REST and an OpenAI-compatible API.

The Modelfile makes the model easier to reuse by packaging its default role, system instructions and generation parameters. The REST API allows a Python application to communicate directly with the local model instead of depending on the command-line interface.

If the same application has to serve around 100 users at the same time, a production serving system such as vLLM becomes more suitable. Many concurrent requests create memory and scheduling challenges, especially because each request needs KV-cache memory. PagedAttention improves memory utilisation, while continuous batching keeps the GPU busy by admitting new requests as existing requests finish.

In general, local Ollama is sufficient for personal projects, development, testing and small private applications. Modelfiles provide reusable model defaults, while the REST and OpenAI-compatible APIs make the model accessible to programs. When concurrent users, throughput, latency and GPU memory efficiency become major requirements, a server designed for high-throughput serving such as vLLM is more appropriate.

7. Result

Thus, the Student Expense and Budget Assistant was designed as a local Ollama application using a custom Modelfile, REST API requests and an OpenAI-compatible endpoint. The analysis demonstrates how a Modelfile provides default behaviour, how program-level prompts can override that behaviour, and why efficient memory management and continuous batching become important when the number of users increases.