from openai import OpenAI
import os
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================
# BASE AGENT
# =========================
class LLM_Agent:
    def __init__(self, model: str = "gpt-4o"):
        self.model = model

    def get_response(self, messages) -> str:
        if self.model.startswith("o3"):
            completion = client.chat.completions.create(
                model=self.model,
                messages=messages
            )
        else:
            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2
            )

        if completion.choices and completion.choices[0].message.content:
            return completion.choices[0].message.content.strip()

        return ""

# =========================
# FORMALIZATION AGENT
# =========================
class Formalization_Agent(LLM_Agent):
    def __init__(self, model: str = "gpt-4o"):
        super().__init__(model)

    def formalize(self, problem: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "Convert the natural language math statement into a Lean 4 theorem type.\n"
                    "STRICT RULES:\n"
                    "- Output ONLY the Lean type\n"
                    "- NO explanation\n"
                    "- NO extra text\n\n"
                    "Examples:\n"
                    "sqrt(2) is irrational → Irrational (Real.sqrt 2)\n"
                    "n+n = 2n → ∀ n : Nat, n + n = 2 * n\n"
                    "n*(m+k) = n*m + n*k → ∀ n m k : Nat, n*(m+k) = n*m + n*k\n"
                )
            },
            {"role": "user", "content": problem}
        ]

        result = self.get_response(messages)

        # Extract clean Lean type
        match = re.search(r"(∀.*|Irrational.*|.*= .*|.*:.*)", result)
        return match.group(0).strip() if match else result.strip()


# =========================
# REASONING AGENT
# =========================
class Reasoning_Agent(LLM_Agent):
    def __init__(self, model: str = "o3-mini"):
        super().__init__(model)

    def analyze_problem(self, problem_description: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Lean 4 reasoning expert.\n"
                    "Break into 3-5 short logical steps.\n"
                    "DO NOT write Lean code.\n"
                    "Be concise."
                )
            },
            {"role": "user", "content": problem_description}
        ]
        return self.get_response(messages)


# =========================
# CODE GENERATION AGENT
# =========================
class Code_Agent(LLM_Agent):
    def __init__(self, model: str = "gpt-4o"):
        super().__init__(model)

    def generate_code(self, problem_description: str, reasoning: str, lean_template: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Lean 4 expert.\n\n"

                    "CRITICAL RULES:\n"
                    "- DO NOT write 'theorem'\n"
                    "- DO NOT write ':='\n"
                    "- DO NOT write 'by'\n"
                    "- DO NOT add imports\n"
                    "- ONLY output the proof body\n\n"

                    "VERY IMPORTANT:\n"
                    "- For polynomial equalities, prefer using: ring"
                    "- If the goal is of the form: ∀ n m k : Nat, ...\n"
                    "  you MUST start with: intro n m k\n"
                    "- Always introduce ALL variables after ∀ using 'intro'\n\n"

                    "STYLE:\n"
                    "- Use Mathlib lemmas\n"
                    "- Prefer: exact <lemma> or rw [lemma]\n"
                    "- Keep it minimal and correct\n\n"

                    "EXAMPLES:\n"
                    "Example 1:\n"
                    "Goal: ∀ n m k : Nat, n*(m+k) = n*m + n*k\n"
                    "Proof:\n"
                    "intro n m k\n"
                    "rw [Nat.mul_add]\n\n"
                    "Example 2:\n"
                    "Goal: Irrational (Real.sqrt 2)\n"
                    "Proof:\n"
                    "exact irrational_sqrt_two"

                    "Example 3:\n"
                    "If goal involves expressions like:\n"
                    "n^2, m^2, (n+m)^2, etc.\n"
                    "→ use: ring\n"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Problem:\n{problem_description}\n\n"
                    f"Reasoning:\n{reasoning}\n\n"
                    f"Template:\n{lean_template}"
                )
            }
        ]
        return self.get_response(messages)

# =========================
# FIX AGENT
# =========================
class Fix_Agent(LLM_Agent):
    def __init__(self, model: str = "gpt-4o"):
        super().__init__(model)

    def fix_code(self, problem_description: str, current_proof: str, error_message: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are fixing Lean 4 proofs.\n\n"

                    "CRITICAL RULES:\n"
                    "- ONLY return corrected proof body\n"
                    "- DO NOT write theorem\n"
                    "- DO NOT write imports\n"
                    "- DO NOT write ':='\n"
                    "- DO NOT write 'by'\n\n"

                    "IMPORTANT:\n"
                    "- If the goal has ∀ n m k, use: intro n m k\n"
                    "- Always introduce ALL variables explicitly\n"
                    "- Use Mathlib lemmas\n"
                    "- Keep it minimal\n\n"

                    "FALLBACK RULE:\n"
                    "- If no direct lemma exists:\n"
                    "  - DO NOT guess lemma names\n"
                    "  - Use contradiction style with valid Lean syntax\n"
                    "  - Example:\n"
                    "    rintro h\n"
                    "    -- derive contradiction using h\n\n"

                    "NEVER output invalid or non-Lean text."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Problem:\n{problem_description}\n\n"
                    f"Current Proof:\n{current_proof}\n\n"
                    f"Lean Error:\n{error_message}"
                )
            }
        ]
        return self.get_response(messages)


# =========================
# TEST BLOCK
# =========================
if __name__ == "__main__":
    agent = Code_Agent()
    # print(agent.generate_code("Prove sqrt(2) is irrational", "", ""))