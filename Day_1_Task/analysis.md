# Day 1 — Plain Chatbot vs Rule-Based Workflow vs AI Agent

## 1. Scenario

This project uses a **Personal Book Library and Reading Goal** scenario.

The application stores a user's private book collection and reading goals in local JSON files. The system can check book information, identify completed books by category, compare completed books with reading goals, and report whether the goals have been reached.

The three approaches use the same scenario but work in different ways:

- **Plain Chatbot:** uses only an LLM and cannot access the private library files.
- **Rule-Based Workflow:** directly reads the files and follows fixed programmed steps.
- **AI Agent:** uses an LLM together with tools and a loop to decide which actions are needed.

---

## 2. Plain Chatbot

The plain chatbot uses an **LLM only**.

It can understand natural-language questions and generate useful general responses, but it does not have access to the user's private book library or reading-goal JSON files.

For example, if the user asks:

> "Have I completed enough Technology books to reach my reading goal?"

the plain chatbot cannot calculate the answer from the user's actual private data because it has no access to the library files.

### Architecture

```text
User
  ↓
LLM
  ↓
Response
```

### Characteristics

- Uses an LLM.
- Does not access private JSON files.
- Does not use external tools.
- Can understand natural-language questions.
- Cannot calculate results from the user's actual private library data.

### Limitation

The chatbot depends only on the information available in the conversation. It cannot independently retrieve or analyze the user's private library data.

---

## 3. Rule-Based Workflow

The rule-based workflow does not need an LLM to make decisions.

It directly reads the private book and reading-goal JSON files and performs a predefined sequence of operations.

### Fixed Execution Path

```text
Load Books
    ↓
Load Reading Goals
    ↓
Find Completed Books
    ↓
Count Completed Books by Category
    ↓
Compare Counts With Goals
    ↓
Generate Report
```

The workflow always follows these programmed steps.

For the sample library data:

| Category     | Completed Books | Goal | Result      |
|--------------|-----------------|------|-------------|
| Self-Help    |         1       |  2   | Not Reached |
| Fiction      |         1       |  2   | Not Reached |
| Technology   |         0       |  3   | Not Reached |
| Productivity |         0       |  1   | Not Reached |
| Finance      |         1       |  2   | Not Reached |

### Characteristics

- Direct access to private JSON files.
- No LLM is required for the decision process.
- Uses predefined functions and rules.
- Produces predictable results.
- Follows the same execution path every time.

### Limitation

The workflow is less flexible because its operations and execution order are programmed in advance. If the user asks for a new type of analysis that was not programmed, the workflow needs to be modified.

---

## 4. AI Agent

The AI agent combines three main components:

**LLM + Tools + Loop**

The LLM understands the user's request and decides which available tool should be used.

The tools provide controlled access to the private book library and reading-goal data.

### Available Tools

The agent can use tools for tasks such as:

- Retrieving the user's books.
- Retrieving reading goals.
- Calculating completed books by category.
- Comparing completed books with reading goals.

### Agent Flow

```text
User Request
     ↓
LLM Understands Request
     ↓
Select Appropriate Tool
     ↓
Execute Tool
     ↓
Observe Tool Result
     ↓
LLM Evaluates Result
     ↓
Another Tool / Final Answer
```

The agent does not need to follow one fixed sequence for every question.

For example, depending on the user's request, it can decide whether it needs book data, goal data, category calculations, or a comparison.

### Characteristics

- Uses an LLM.
- Uses tools to access private data.
- Can perform multiple steps.
- Can dynamically select the next action.
- Uses tool results as observations.
- Produces a final answer after completing the required actions.

### Limitation

Because the LLM decides which tools to use, the agent requires proper tool definitions, validation, error handling, and clear instructions.

---

## 5. Comparison

| Basis               | Plain Chatbot           | Rule-Based Workflow              | AI Agent                   |
|---------------------|-------------------------|----------------------------------|----------------------------|
| Main component      | LLM                     | Programmed functions and rules   | LLM + Tools + Loop         |
| Private-data access | No                      | Yes                              | Yes, through tools         |
| LLM used            | Yes                     | No                               | Yes                        |
| Tool usage          | None                    | Fixed functions                  | Dynamically selected tools |
| Decision mechanism  | LLM generates response  | Predefined rules                 | LLM selects actions        |
| Execution path      | Single response         | Fixed                            | Dynamic                    |
| Multi-step handling | Limited                 | Fixed steps                      | Dynamic steps              |
| Flexibility         | Conversational          | Limited to programmed operations | High                       |
| Predictability      | Depends on LLM response | High                             | Depends on LLM and tools   |
| Best suited for     | General conversation    | Fixed and repeatable tasks       | Flexible data-driven tasks |

---

## 6. Example Task

Consider the user request:

> "Check my reading progress and tell me whether I have reached my goals for each category."

### Plain Chatbot

The plain chatbot can understand the question, but it cannot inspect the private book and goal files.

Therefore, it cannot calculate the user's real progress.

### Rule-Based Workflow

The workflow performs its predefined operations:

```text
Read Books
   ↓
Read Goals
   ↓
Find Completed Books
   ↓
Count by Category
   ↓
Compare With Goals
   ↓
Generate Result
```

It can produce the result because the required operations are already programmed.

### AI Agent

The agent can decide which tools are required for the request.

A possible execution is:

```text
Understand Request
      ↓
Get Books
      ↓
Get Reading Goals
      ↓
Calculate Category Progress
      ↓
Compare With Goals
      ↓
Generate Final Answer
```

The important difference is that the agent's next action is selected according to the user's request rather than always following one fixed workflow.

---

## 7. Suitability

### Plain Chatbot

Suitable when:

- The user needs general information.
- No private data needs to be accessed.
- Tool usage is not required.

### Rule-Based Workflow

Suitable when:

- The task is predictable.
- The steps are known in advance.
- The same operations need to be repeated reliably.
- Deterministic results are important.

### AI Agent

Suitable when:

- The task requires private data.
- Multiple operations may be needed.
- Different user requests may require different tools.
- The execution path cannot always be fixed beforehand.

For this book-library scenario, the AI agent demonstrates how an LLM can combine reasoning with controlled tool access and multiple steps.

---

## 8. Key Difference

The main difference between the three approaches is **who decides what happens next**.

```text
Plain Chatbot
    ↓
LLM generates a response

Rule-Based Workflow
    ↓
Programmed rules decide the steps

AI Agent
    ↓
LLM decides which tool/action is needed
    ↓
Tool provides an observation
    ↓
LLM decides what to do next
```

So:

- **Plain Chatbot = LLM response**
- **Rule-Based Workflow = Fixed programmed process**
- **AI Agent = LLM + Tools + Dynamic Loop**

---

## 9. Conclusion

The three approaches solve problems differently.

A **plain chatbot** mainly understands the user's message and generates a response, but it cannot access the private book-library data.

A **rule-based workflow** can access the private data and produce reliable results, but it follows a predefined sequence of operations.

An **AI agent** combines an LLM with tools and an execution loop. It can select the actions needed for a request, use private data through controlled tools, observe the results, and continue until it can provide the final answer.

This project demonstrates the progression from:

```text
LLM Only
   ↓
Fixed Workflow
   ↓
LLM + Tools + Dynamic Loop
```

The important concept is that an AI agent is not simply a chatbot. It can **decide actions, use tools, observe results, and continue working toward a goal**.
