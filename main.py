import os
from typing import Dict, List, Tuple
from src.agents import Reasoning_Agent, Code_Agent, Fix_Agent, Formalization_Agent
from src.lean_runner import execute_lean_code

LeanCode = Dict[str, str]


# =========================
# CLEAN PROOF
# =========================
def clean_proof(proof: str) -> str:
    lines = proof.split("\n")
    cleaned = []

    for i, line in enumerate(lines):
        line = line.strip()

        if not line:
            continue

        # remove garbage words
        if i == 0 and line.lower() in ["proof", "prooftree"]:
            continue

        cleaned.append(line)

    return "\n".join(cleaned)


# =========================
# CLEAN BLOCK
# =========================
def clean_block(text):
    return text.replace("```lean", "").replace("```", "").strip()


# =========================
# PARSER (PROOF ONLY)
# =========================
def parse_llm_output(response: str):
    proof = ""

    blocks = response.split("```")
    for block in blocks:
        if any(t in block for t in ["exact", "simp", "rw", "ring", "intro"]):
            proof = block
            break

    return clean_proof(clean_block(proof))


# =========================
# MAIN WORKFLOW (AGENT LOOP)
# =========================
def main_workflow(problem_description: str, task_lean_code: str = "") -> LeanCode:

    print("\n" + "=" * 60)
    print("🧠 USER INPUT")
    print("=" * 60)
    print(problem_description)

    # -------------------------------
    # STEP 0: FORMALIZATION
    # -------------------------------
    formalizer = Formalization_Agent()

    print("\n" + "=" * 60)
    print("🔤 STEP 0: FORMALIZATION")
    print("=" * 60)

    theorem_type = formalizer.formalize(problem_description)
    print("Formalized type:\n", theorem_type)

    reasoning_agent = Reasoning_Agent()
    code_agent = Code_Agent()
    fix_agent = Fix_Agent()

    # -------------------------------
    # STEP 1: REASONING
    # -------------------------------
    print("\n" + "=" * 60)
    print("🤖 STEP 1: REASONING")
    print("=" * 60)

    reasoning = reasoning_agent.analyze_problem(problem_description)
    print(reasoning)

    # -------------------------------
    # TEMPLATE
    # -------------------------------
    if task_lean_code.strip() == "":
        base_template = f"""import Mathlib

theorem user_theorem : {theorem_type} := by
  {{proof}}
"""
    else:
        base_template = task_lean_code

    # -------------------------------
    # AGENT LOOP
    # -------------------------------
    max_attempts = 3
    generated_proof = ""
    last_error = ""

    for attempt in range(max_attempts):

        print("\n" + "=" * 60)
        print(f"🔁 ATTEMPT {attempt + 1}")
        print("=" * 60)

        # GENERATE OR FIX
        if attempt == 0:
            response = code_agent.generate_code(
                problem_description,
                reasoning,
                base_template
            )
        else:
            response = fix_agent.fix_code(
                problem_description,
                generated_proof,
                last_error
            )

        print("\n--- RAW LLM OUTPUT ---\n")
        print(response)

        # PARSE
        generated_proof = parse_llm_output(response)

        print("\n--- PARSED PROOF ---\n")
        print(generated_proof)

        # BUILD LEAN FILE
        indented_proof = "\n  ".join(generated_proof.split("\n"))
        modified_code = base_template.replace("{proof}", indented_proof)

        print("\n--- FINAL LEAN CODE ---\n")
        print(modified_code)

        # RUN LEAN
        print("\n⚙️ Running Lean...\n")
        result = execute_lean_code(modified_code)
        print(result)

        if "error" not in result.lower():
            print("\n✅ SUCCESS!")
            break

        print("\n❌ FAILED — retrying...")
        last_error = result

    return {
        "proof": generated_proof,
        "lean_code": modified_code
    }


# =========================
# FILE HELPERS
# =========================
def get_problem_and_code_from_taskpath(task_path: str) -> Tuple[str, str]:
    with open(os.path.join(task_path, "description.txt"), "r") as f:
        desc = f.read()

    with open(os.path.join(task_path, "task.lean"), "r") as f:
        code = f.read()

    return desc, code


def get_unit_tests_from_taskpath(task_path: str) -> List[str]:
    with open(os.path.join(task_path, "tests.lean"), "r") as f:
        return f.read()


def get_task_lean_template_from_taskpath(task_path: str) -> str:
    with open(os.path.join(task_path, "task.lean"), "r") as f:
        return f.read()


# =========================
# CLI MODE
# =========================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🤖 Lean 4 Agentic AI (Interactive Mode)")
    print("=" * 60)

    problem = input("\n🧠 Enter your problem:\n> ")

    result = main_workflow(problem, "")

    print("\n" + "=" * 60)
    print("📦 FINAL OUTPUT")
    print("=" * 60)

    print("\n✅ Final Verified Proof:\n")
    print(result["proof"] if result["proof"] else "[No proof generated]")

    print("\n📜 Lean Code Used:\n")
    print(result["lean_code"] if result.get("lean_code") else "[No code generated]")