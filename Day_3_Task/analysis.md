# From Prompt to Action: LLMs, Tools, and Agents

## 1. Scenario

For this task, I created a simple **College AI Workshop Information Assistant**.

The workshop information is stored in a local text file called `event_info.txt`. The information includes the workshop date, time, room, registration fee, and other details.

I used one tool called `read_event_info()`. The purpose of this tool is to read the event information when the LLM needs information that is not available from its own knowledge.

---

## 2. What is an LLM?

A Large Language Model (LLM) is a model trained on a large amount of text. It can answer many questions using patterns and information learned during training.

For example, if I ask the model:

> "Write a two-line welcome message for students attending a workshop."

It can answer directly without using any external tool.

However, the model does not automatically know the private information in my `event_info.txt` file. If I ask:

> "What is the registration fee for my AI Workshop?"

the model may not know the correct answer. It could guess or give an answer based on the information it already knows.

This shows that an LLM can generate text very well, but it cannot automatically access information outside its available context.

---

## 3. What is an Agent?

An agent is an LLM that can use tools to perform actions or get additional information.

A normal LLM simply receives a question and generates an answer.

In my example, the tool-enabled LLM works differently. When I ask about the workshop fee, it can recognise that it needs information from the event file, call `read_event_info()`, receive the result, and then use that result to answer.

So the important difference is that an agent can take an additional action instead of only generating text.

---

## 4. What is a Tool and a Tool Call?

A **tool** is an external function that the LLM can use when it needs information or needs to perform an operation.

My tool is:

```python
read_event_info()
```

It reads the workshop information from the local file and returns it as text.

The model is given the tool's schema, which tells it the tool's:

* name
* description
* parameters

The model needs this information so it knows what the tool does and when it should use it.

A **tool call** is the actual request made by the model to run that tool.

For example:

```text
Tool call: read_event_info({})
```

The tool then returns the workshop information to the model.

---

## 5. How the Tool Call Works

The process in my project is simple:

1. The user asks a question.
2. The LLM receives the question and the available tool.
3. The LLM decides whether the tool is needed.
4. If needed, it calls `read_event_info()`.
5. The tool reads `event_info.txt`.
6. The tool returns the information as text.
7. The LLM receives the result.
8. The LLM uses the result to give the final answer.

For example, when I asked for the workshop registration fee, the model called the tool and then answered using the information returned by the tool.

---

## 6. Why Return Text Instead of Raising an Error?

A tool should preferably return a text result even when something goes wrong.

For example, instead of stopping the whole program with an exception, the tool could return:

```text
Event information could not be found.
```

The LLM can then see the message and explain the problem to the user.

This keeps the agent running and allows the LLM to handle the failure more naturally.

---

## 7. Comparison

| Basis                       | Plain LLM                                 | LLM with One Tool                                 |
| --------------------------- | ----------------------------------------- | ------------------------------------------------- |
| Source of answer            | Trained knowledge and conversation        | Trained knowledge + tool result                   |
| Fetch external information? | No                                        | Yes, through the tool                             |
| Numeric/factual reliability | May guess when information is unavailable | More reliable when the tool has the correct data  |
| Transparency                | We only see the final answer              | We can also see the tool call and result          |
| Speed / cost                | Usually faster and simpler                | Slightly more processing because of the tool call |

---

## 8. Observations

I tested three questions.

### Question 1

**"What is the registration fee for the AI Workshop?"**

This information is stored in the event file, so the tool is needed.

The plain LLM does not have access to my private event file and may not know the correct fee.

The tool-enabled LLM called:

```text
read_event_info()
```

and used the returned information to answer the question.

### Question 2

**"What room is the AI Workshop held in?"**

This also requires the event file.

The tool-enabled version called the tool and used the returned room information in its answer.

### Question 3

**"Write a two-line welcome message for workshop participants."**

This does not require the event file.

The LLM can generate this directly from its language ability, so there is no need to call the tool.

This showed that the model does not have to use a tool for every question.

---

## 9. When is a Tool Necessary?

A plain LLM is enough for tasks such as writing, rewriting, explaining common concepts, or generating ideas.

A tool becomes useful when the answer depends on information or an operation outside the model's normal knowledge. Examples include private files, current information, calculations, databases, APIs, or external services.

In my scenario, the LLM was enough for writing a welcome message, but the tool was necessary for getting the actual workshop information from my local file.

---

## 10. Conclusion

This task helped me understand the difference between a normal LLM and an LLM that can use tools.

An LLM is good at generating and understanding language, but it cannot automatically access every piece of information.

Adding even one simple tool gives the model a way to get information from outside its own knowledge. The model can decide when the tool is useful, call it, receive the result, and use that result in its final response.

Therefore, a plain prompt is suitable for many language-based tasks, while tools become important when the task requires reliable external information or an operation that the LLM cannot perform by itself.
