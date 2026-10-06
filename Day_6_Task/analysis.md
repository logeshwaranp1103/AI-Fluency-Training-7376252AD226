# Day 6 — Reliable Tool Calling: Student Expense & Budget Assistant

## 1. Scenario

For this task I chose a **student expense and budget assistant**. The expense records and monthly budgets are stored locally in Python data structures.

The available categories are:

- Food
- Transport
- Entertainment
- Education

The assistant has three tools:

1. `get_spending(category)` — gets total spending for a category.
2. `get_budget(category)` — gets the monthly budget for a category.
3. `calculator(expression)` — safely calculates arithmetic expressions.

Example stored data includes Food expenses of Rs. 120, Rs. 180 and Rs. 100, giving total Food spending of Rs. 400. The Food budget is Rs. 400.

The important point is that the model does **not** directly run Python functions. It generates a tool-call message. My code receives that generated text, checks it, and only then executes the requested function.

---

# 2. Explanation of Concepts

## 2.1 Chat Completions format

The Chat Completions API sends a request containing fields such as:

- `model` — the model to use.
- `messages` — system, user, assistant and tool messages.
- `tools` — the available function definitions.
- `temperature` — controls randomness.
- `max_tokens` — limits the generated response length.

The response contains `choices`. Each choice has a `message` and a `finish_reason`.

For my expense assistant, a request can look conceptually like:

```text
model + messages + tools
        ↓
     model
        ↓
assistant message + finish_reason
```

The important `finish_reason` values are:

| finish_reason | Meaning | My code's reaction |
|---|---|---|
| `stop` | The model finished normally. | If there is no tool call, return the final answer. |
| `length` | The reply was cut off by the token limit. | Increase `max_tokens` and retry, up to the limit. |
| `tool_calls` | The model wants one or more tools. | Process every tool call, send the results back, and continue the loop. |

`message.content` can be empty when the model wants a tool because the useful part of the assistant message is the `tool_calls` field. In that case, the model is asking my program to perform an action instead of giving the final natural-language answer.

---

## 2.2 What “OpenAI-compatible” means

An OpenAI-compatible server exposes an API that follows the same general request and response format as the OpenAI client expects.

This allows the same Python client style to communicate with providers such as:

- Ollama
- vLLM
- Groq
- Hugging Face

The main change is usually the server URL and the model/API key configuration.

In my project, the provider is selected through `.env`:

```text
PROVIDER=ollama
MODEL=qwen3:8b
```

For Ollama, the client uses:

```text
http://localhost:11434/v1
```

A compatible API does **not** promise that every server and model supports every feature identically. For example, strict structured-output schema support can vary between providers and models. Therefore, compatibility means the API interface is similar; it does not mean identical model behaviour or identical feature support.

---

## 2.3 Streaming and why I did not use it

Streaming sends the model response in small chunks as it is generated instead of waiting for the complete response.

It improves:

- perceived response speed;
- user experience for long answers;
- ability to show partial text immediately.

Inside an agent loop, streaming is usually switched off because the program needs a complete assistant message and complete tool-call arguments before validating and executing them. Handling partial tool-call JSON adds unnecessary complexity for this small task.

The Responses API style is different from Chat Completions because it uses a newer response/item-oriented interaction model, while Chat Completions uses a sequence of messages and choices. This course stays with Chat Completions because it directly demonstrates the message → tool call → tool result → message loop required for this lab.

Streaming, the Responses API and multi-agent behaviour were not required for my implementation.

---

## 2.4 Five steps of one tool call

For my expense assistant, one tool call follows these steps:

### Step 1 — Send the request

My code sends the user's question, available messages and tool schemas to the model.

### Step 2 — Model generates a tool call

For example, for:

> How much did I spend on Food?

the model may generate a call similar to:

```json
{
  "name": "get_spending",
  "arguments": "{\"category\":\"Food\"}"
}
```

### Step 3 — My code validates the call

The handler:

1. parses the generated JSON;
2. checks whether the tool exists;
3. checks required arguments, types, enum values and extra arguments.

### Step 4 — My code runs the function

The Python function `get_spending("Food")` runs and returns:

```text
400
```

The model does **not** execute the Python function.

### Step 5 — Send the result back

My code adds a tool message containing the result and asks the model to continue. The model can then produce the final answer:

> You spent Rs. 400 on Food.

This matters because a model's generated tool call must be treated as **untrusted input**. The model suggests what should be done; my program decides whether that request is valid before the function runs.

---

# 3. Tool definitions and schemas

My tool definitions contain the following important schema parts:

| Part | Purpose in my scenario | Mistake it helps prevent |
|---|---|---|
| `description` | Explains what the tool does and what values are expected. | Reduces guessing and misuse. |
| `properties` | Defines available arguments such as `category` or `expression`. | Prevents unclear argument structure. |
| `enum` | Restricts category to Food, Transport, Entertainment or Education. | Prevents values such as `Shopping`. |
| `required` | Requires the needed argument. | Prevents a missing `category`. |
| `additionalProperties: false` | Rejects arguments not defined by the tool. | Prevents invented fields such as `month`. |
| `strict` | When supported by a structured-output schema, forces the output to follow the declared structure. | Prevents a response from having an unexpected JSON shape. |

The project keeps a single `SCHEMAS` dictionary generated from `TOOLS`. Therefore, the same schema information sent to the model is also used by the local validator.

### Tool choice

`tool_choice` can control tool selection:

| Value | Meaning |
|---|---|
| `auto` | Model decides whether to call a tool. |
| `none` | Model must not call a tool. |
| `required` | Model must call a tool. |
| Named function | Forces a particular function when supported. |

For my general expense assistant, `auto` is the best choice because some questions need tools while simple questions such as "Give me one short budgeting tip" do not.

---

# 4. JSON mode vs schema mode

JSON mode asks the model to return valid JSON, but it does not necessarily force my exact field structure.

Schema mode goes further by defining the exact fields and types expected.

| | JSON mode | Schema mode |
|---|---|---|
| Valid JSON | Yes | Yes |
| Exact field names | Not necessarily | Yes |
| Exact field types | Not necessarily | Yes |
| Additional fields can be restricted | Not necessarily | Yes, with the schema |
| Provider support | Generally broader | More provider/model dependent |

For example, if I ask:

> I spent money on food and want to know whether I am over my food budget.

I can use structured output to extract:

```json
{
  "category": "Food",
  "needs_budget_lookup": true,
  "needs_spending_lookup": true
}
```

I would use **tool calling** when the program must fetch or calculate something, such as reading the Food spending or calculating the difference between spending and budget.

I would use **structured output** when my program mainly needs the model to extract fields from a sentence.

A perfectly shaped JSON response still does not guarantee a correct answer. The JSON can have the correct structure but contain an incorrect value. For example:

```json
{
  "category": "Food",
  "needs_budget_lookup": false,
  "needs_spending_lookup": true
}
```

may be syntactically perfect but logically wrong for the question if a budget comparison is clearly requested.

---

# 5. Parallel tool calls

Parallel tool calls happen when one assistant response contains two or more tool calls.

For example, the question:

> Compare my Food spending and budget, and also compare my Transport spending and budget.

may cause the model to request multiple data lookups at once.

My loop does not assume there is only one call. It loops through:

```python
for call in message.tool_calls:
```

For every call it creates exactly one:

```text
role = tool
tool_call_id = the call's ID
content = result
```

This is important because the server expects every tool call ID in the assistant message to receive a corresponding tool result. If one `tool_call_id` is left unanswered, the API can reject the conversation with an error.

The question that is most likely to create parallel calls in my scenario is:

> Compare my Food spending and budget, and also compare my Transport spending and budget.

The exact behaviour depends on the local model, so I record the actual result when running the agent.

---

# 6. Failures handled by my implementation

Tool calls are generated by the model, so they can be malformed.

My implementation handles:

|          Failure        |                         What my code does                                  |
|-------------------------|----------------------------------------------------------------------------|
| Invalid JSON            | Returns an error message asking the model to send valid JSON.              |
| Unknown tool            | Lists the available tools.                                                 |
| Missing argument        | Names the missing argument and expected arguments.                         |
| Wrong type              | Says what type was expected and what type arrived.                         |
| Value outside enum      | Shows the allowed enum values.                                             |
| Invented argument       | Rejects the extra argument and lists allowed arguments.                    |
| Truncated reply         | Detects `finish_reason == "length"` and retries with a larger token limit. |
| Repeated identical call | Counts identical name/argument pairs and stops after three.                |

The validator therefore does not simply say "invalid input". It produces a useful message such as:

```text
Argument 'category' must be one of
['Food', 'Transport', 'Entertainment', 'Education'],
got 'Shopping'.
```

This gives the model information it can use to repair the request.

---

# 7. Repair pattern

The repair pattern is:

```text
Model
  ↓
tool call
  ↓
parse
  ↓
look up tool
  ↓
validate
  ↓
execute
  ↓
tool result
  ↓
Model
  ↓
final answer
```

Each stage returns a string instead of raising an exception because the model needs to be able to read the failure and try again.

For example, if the model sends:

```json
{"category": "Shopping"}
```

the validator returns an error message. The program sends that message as the tool result, so the model can correct itself.

A truncated response is different. `finish_reason = length` means the generation itself was cut off by the token limit. There may not be a complete tool call or final answer to repair. Therefore, the program increases `max_tokens` and retries.

A malformed tool call is different because the call exists but contains invalid generated input. That failure can be returned to the model as a recoverable tool result.

---

# 8. Fault injection

Fault injection means deliberately giving the program the kind of bad input that a real model might produce.

My `inject_faults.py` creates fake tool-call objects and passes them directly to `handle_tool_call`.

It does not need:

- a model;
- an API request;
- internet access.

This is useful because the validator and handler are ordinary Python code. Their behaviour can be tested deterministically.

The injected faults include:

1. good call;
2. invalid JSON;
3. unknown tool;
4. missing required argument;
5. wrong type;
6. enum value outside the allowed list;
7. invented extra argument;
8. JSON array instead of JSON object;
9. unsafe calculator expression.

This shows that many agent bugs actually live at the boundary between generated model output and application code. The model does not need to fail naturally for the program's safety guards to be tested.

A stricter schema can prevent an invented extra argument such as:

```text
{"category": "Food", "month": "September"}
```

because `additionalProperties` is false.

A stricter schema cannot guarantee that the model will choose the right tool for the user's intention or produce a semantically correct final answer.

---

# 9. Comparison: Tool Calling vs Structured Outputs

| Basis | Tool calling | Structured outputs |
|---|---|---|
| What the model is asked to do | Request an action/function using arguments. | Return data in a defined format. |
| Who performs the action or produces final data | My Python code performs the tool action; the model produces the final explanation. | The model produces the structured data. |
| How the shape is controlled | Function parameters and JSON Schema. | JSON mode or a JSON Schema. |
| What can still go wrong | Invalid arguments, wrong tool, repeated calls, incorrect reasoning. | Correct JSON shape can still contain incorrect values or interpretation. |
| How my code guards against it | Parse, tool lookup, validation, safe execution, retries and repeat detection. | Parse JSON and validate/use the returned fields. |
| Support across servers/models | Tool support is generally available in compatible APIs, but behaviour varies. | Basic JSON mode is often easier; strict schema mode varies more by provider/model. |
| My choice for fetch/calculate | **Tool calling**, because Python must access stored data or perform the calculation. | Not my first choice because structured output does not itself perform the action. |
| My choice for extracting fields | **Structured output**, because the program needs predictable fields from a sentence. | **Structured output**, because exact fields such as category and boolean flags are the desired result. |

---

# 10. Observation

The following tables are the observation record for the implementation. Exact model behaviour can vary between Ollama models and providers, so model-dependent fields should be updated with the output produced during the actual run.

## 10.1 Fault table

| Injected fault | Message returned | Run continued? |
|---|---|---|
| Invalid JSON | `Argument error: invalid JSON ... Send valid JSON for 'get_spending'.` | Y |
| Unknown tool | `Unknown tool: send_email. Available tools: get_spending, get_budget, calculator.` | Y |
| Missing required | `Argument error: Missing required argument 'category'. Expected: category.` | Y |
| Wrong type | `Argument 'category' must be a string, but got int: 101.` | Y |
| Value outside enum | `Argument 'category' must be one of ['Food', 'Transport', 'Entertainment', 'Education'], got 'Shopping'.` | Y |
| Invented argument | `Unexpected argument(s): month. Allowed: category.` | Y |
| Unsafe expression | `Calculator error: Unsupported expression...` | Y |
| Own fault 1 — JSON array | `Argument error: Arguments must be a JSON object.` | Y |
| Own fault 2 — unsafe expression | Calculator rejects the expression instead of executing injected code. | Y |

### Observation

The important result is that the handler returns a string for each fault instead of allowing the program to crash. The message also explains the expected input wherever possible.

---

# 11. Agent behaviour

The following are the questions used by `robust_agent.py`.

| Question | Expected tool behaviour | Actual steps | Actual tool calls | Parallel? | finish_reason = length? |
|---|---|---:|---|---|---|
| How much did I spend on Food? | One `get_spending` call. | Record from run | Record from run | Record from run | Record from run |
| Compare Food spending/budget and Transport spending/budget. | Multiple spending/budget lookups, possibly in parallel. | Record from run | Record from run | Record from run | Record from run |
| Should I reduce my shopping spending? | Model should encounter an invalid category and receive the allowed categories. | Record from run | Record from run | Record from run | Record from run |
| Give me one short budgeting tip for a student. | No tool should be required. | Record from run | None expected | No | Record from run |

The exact number of steps and whether the local model sends parallel calls depend on the selected model and provider. These fields should be filled from the terminal output rather than guessed.

---

# 12. Before and after the guards

The guarded implementation has four stages:

```text
Parse → Look up → Validate → Execute
```

Without these guards, malformed arguments can reach Python functions directly and may produce exceptions or incorrect behaviour.

With the guards:

| Behaviour | Without guards / simple agent | Guarded agent |
|---|---|---|
| Invalid JSON | Can fail while parsing. | Converted into a recoverable message. |
| Unknown tool | Can fail during lookup. | Lists available tools. |
| Missing argument | Can cause a function error. | Validator explains the missing field. |
| Wrong type | Can cause unexpected behaviour. | Validator rejects it before execution. |
| Extra argument | Can cause `unexpected keyword argument`. | Validator rejects it first. |
| Repeated failing call | Can loop. | Stops after three identical calls. |

For the ME404-style equivalent in this scenario, an invalid category is returned with the valid category list instead of allowing an endless tool loop.

---

# 13. Structured-output observations

`structured_demo.py` tests the same extraction question in three ways.

| Case | Expected observation |
|---|---|
| No constraint | The model may return prose or JSON wrapped in prose. Parsing is not guaranteed. |
| JSON mode | The response should be valid JSON, but the exact fields are not guaranteed by JSON mode alone. |
| Schema mode | If supported by the provider/model, the response should follow the declared fields and types. If unsupported, the script records the error. |

Strict schema support is provider/model dependent. Therefore, an error in schema mode is recorded as a compatibility finding rather than being treated as a code failure.

---

# 14. Suitability and Conclusion

For this scenario, the most important distinction is that the model's tool call is **generated text**. It is not trusted just because it came from an LLM. My Python program must parse it, check the requested tool, validate its arguments and only then execute the function.

The faults that can be tested deterministically are especially useful because they do not depend on waiting for a model to behave badly. Fault injection proves that the guard itself works.

The single most important guard is the **argument validation before execution**. It stops missing arguments, wrong types, invalid enum values and invented arguments from reaching the actual function. Repeat detection is also important because a model can otherwise keep requesting the same failing operation.

For fetching or calculating real data, I would use **tool calling** because the application needs to perform an actual function. For extracting fields from a natural-language sentence, I would use **structured outputs** because the desired result is predictable data rather than an external action.

In general, a model's tool call can never be trusted as it arrives because it is generated by a probabilistic model. Every reply containing tool calls must be processed carefully: parse the arguments, identify the tool, validate the arguments, execute safely, return one result for every tool-call ID, and continue or stop according to the loop guards.

A schema can prevent structural mistakes such as missing required fields, invalid enum values and unexpected arguments. It cannot prevent every semantic mistake or guarantee that the model selected the right action.

Deliberate fault injection provides a repeatable way to test these protections. Instead of waiting for a model to randomly generate an invalid call, the test directly supplies invalid calls and verifies that the handler returns useful messages without crashing.

Therefore, reliable agentic tool calling is not just about giving an LLM tools. It is about putting a validation and recovery boundary between generated model output and the real functions that can change or access data.
