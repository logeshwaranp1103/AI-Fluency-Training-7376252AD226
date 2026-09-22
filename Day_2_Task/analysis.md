# Agentic AI: Foundations and Open-Source Practice

## Day 2 – Reasoning and Acting

### Scenario: College Library Study Planning

For this task, I chose a simple **college library study planning** scenario. The questions involve study-time calculations, seat calculations, ordering, and one question that requires external library information.

---

## 1. Direct Prompting

Direct prompting gives the question directly to the AI and asks for an answer. The model answers using the knowledge and reasoning available to it.

It does not show its reasoning and does not use any external tool.

For example, when asked how much study time is left after studying different subjects, it directly gives the answer.

The main limitation is that it cannot get new information from an external source. If the question needs current library timings, direct prompting cannot check the actual timing.

---

## 2. Chain-of-Thought

Chain-of-Thought prompting asks the model to solve a problem step by step before giving the final answer.

This is useful for questions involving calculations or multiple reasoning steps. For example, the library seat question requires calculating fractions of 48 seats.

However, Chain-of-Thought still does not automatically use an external tool. It can reason about information given in the question, but it cannot fetch a current library closing time by itself.

Therefore, it can improve multi-step reasoning but cannot provide missing external facts.

---

## 3. ReAct Agent

ReAct means **Reasoning and Acting**.

A ReAct agent follows a cycle:

**Thought → Action → Observation → Thought → Final Answer**

For the library scenario, the agent can identify that it needs the library's closing time. It calls the library-hours tool, observes the returned information, and then uses that information to calculate whether a 3-hour study session is possible.

This makes ReAct useful when a question requires both reasoning and external information.

---

## 4. Comparison Table

| Basis                  | Direct Prompting        | Chain-of-Thought          | ReAct Agent                                      |
| ---------------------- | ----------------------- | ------------------------- | ------------------------------------------------ |
| Reasoning depth        | Basic                   | Step-by-step              | Step-by-step with actions                        |
| Tool usage             | No                      | No                        | Yes                                              |
| Multi-step reliability | Lower for complex tasks | Better                    | Better when tools are needed                     |
| Transparency           | Final answer only       | Shows requested steps     | Shows actions and observations                   |
| Speed / cost           | Fast and low cost       | Slower than direct        | Usually slower because of tool calls             |
| Consistency            | Usually consistent      | Can vary with temperature | Can vary depending on tool results and reasoning |

---

## 5. Self-Consistency Observation

For the self-consistency experiment, the same library seat question was run **5 times with temperature 0.8**.

The question was:

> A library has 48 seats. 3/8 of the seats are occupied by first-year students and 1/4 are occupied by second-year students. How many seats are occupied?

The correct calculation is:

* First-year students = 48 × 3/8 = 18
* Second-year students = 48 × 1/4 = 12
* Total occupied seats = 18 + 12 = **30**

The majority answer is expected to be **30 seats** if the runs produce the same correct result.

At temperature 0, the model normally produces much more consistent answers because randomness is reduced.

---

## 6. Suitability Analysis

For this library scenario, **ReAct is the most suitable when current library information is required**, because it can use a tool and then reason using the result.

Direct prompting is suitable for simple questions where all required information is already provided.

Chain-of-Thought is useful for calculations and problems that require several reasoning steps but do not need external information.

ReAct is useful when the problem requires both reasoning and interaction with external tools.

---

## 7. Conclusion

The three approaches are useful for different types of problems.

**Direct prompting** is suitable for simple and straightforward questions where no external information is required.

**Chain-of-Thought** is useful for problems that require multiple reasoning steps, such as calculations and logical questions.

**ReAct** is useful for more practical tasks where the AI needs to reason, use a tool, observe the result, and continue working until it reaches an answer.

Therefore, the main difference is that direct prompting answers directly, Chain-of-Thought focuses on step-by-step reasoning, and ReAct combines reasoning with tool usage.
