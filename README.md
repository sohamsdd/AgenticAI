# 🧠 LLM-Based Agentic AI for Iterative Reasoning & Proof Verification

An Agentic AI system that combines Large Language Models (LLMs) with the **Lean 4** theorem prover to automatically generate, verify, and iteratively refine mathematical proofs.

---

## 🚀 Overview

This project implements an agent-based pipeline where an LLM does not just produce answers once, but:

- 🧠 Reasons about the problem
- ✍️ Generates Lean proofs
- ⚙️ Verifies correctness using Lean
- 🔁 Fixes errors iteratively using feedback

This creates a **neuro-symbolic system** combining:
- Neural reasoning (LLMs)
- Formal verification (Lean)

---

## 🎯 Key Features

- ✅ Natural language → Lean theorem formalization
- 🤖 Multi-agent architecture (reasoning, generation, fixing)
- 🔁 Iterative retry loop with error feedback
- ⚙️ Lean-based formal proof verification
- 📦 Modular and extensible pipeline

---

## 🧠 System Architecture

```
User Input
   ↓
Formalization Agent
   ↓
Reasoning Agent
   ↓
Code Generation Agent
   ↓
Lean Verification (lean_runner.py)
   ↓
Error Feedback
   ↓
Fix Agent
   ↓
Repeat (until success)
```

---

## 📁 Project Structure

```
AgenticAI/
│
├── src/
│   ├── main.py           # Orchestrates full agent workflow
│   ├── agents.py         # All LLM agents (formalization, reasoning, code, fix)
│   └── lean_runner.py    # Executes Lean code and captures output/errors
│
├── tasks/
│   └── task_id_2/        # Example problem (sqrt(2) irrational)
│
├── tests/
│   └── tests.py          # Runs tasks and evaluates results
│
├── README.md
├── requirements.txt
├── lakefile.toml         # Lean project config
└── lean-toolchain        # Lean version
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/sohamsdd/AgenticAI.git
cd AgenticAI
```

### 2. Setup Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Setup OpenAI API key

```bash
export OPENAI_API_KEY="your_api_key_here"
```

### 4. Setup Lean (if not installed)

```bash
lake update
lake build
```

---

## ▶️ Running the Project

### 🔹 Interactive Mode

```bash
python -m src.main
```

**Example input:**
```
prove n*(m+k) = n*m + n*k
```

### 🔹 Run predefined task

```bash
python -m tests.tests task_id_2
```

---

## 🧪 Example Output

**Input**
```
prove n^2 - m^2 = (n - m)*(n + m)
```

**Generated Lean Proof**
```lean
intro n m
ring
```

**Output**
```
✅ Lean code executed successfully.
```

---

## 🧠 Core Components

### 🔹 `main.py`
- Controls full pipeline
- Handles retries and error feedback
- Builds Lean code dynamically

### 🔹 `agents.py`
Implements multiple LLM agents:
- **Formalization Agent** → Converts natural language to Lean types
- **Reasoning Agent** → Breaks problem into steps
- **Code Agent** → Generates Lean proof
- **Fix Agent** → Repairs proof using Lean errors

### 🔹 `lean_runner.py`
- Writes Lean code to file
- Runs Lean using `lake`
- Captures success or compiler errors

---

## ⚠️ Limitations

- Limited support for complex proofs (e.g., induction-heavy theorems)
- No structured goal-state extraction from Lean
- Full proof regeneration instead of partial editing
- No lemma retrieval from Mathlib

---

## 🚀 Future Improvements

- 🔍 Goal-state extraction from Lean
- 📚 Mathlib lemma retrieval (RAG integration)
- 🧩 Step-wise proof editing instead of full regeneration
- 📊 Benchmarking and evaluation framework

---

## 🧠 Key Learnings

- Difference between LLM generation vs formal correctness
- Designing agentic workflows with feedback loops
- Integration of symbolic systems (Lean) with neural models
- Importance of prompt engineering + error handling

---

## 📌 Technologies Used

- Python
- OpenAI GPT models
- Lean 4 + Mathlib
- WSL (Linux environment)
