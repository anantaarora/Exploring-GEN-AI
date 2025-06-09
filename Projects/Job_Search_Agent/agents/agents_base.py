import openai
from typing import Any
import re

class Agent:
    def __init__(self, name: str, instructions: str, model: str, output_type: Any):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.output_type = output_type

    async def run(self, prompt: str):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.instructions},
                {"role": "user", "content": prompt}
            ]
        )

        content = response["choices"][0]["message"]["content"]
        print(f"[{self.name}] Output:\n", content)

        # --- Clean up code block markers if present ---
        # Remove triple backticks and optional 'json' after them
        content = re.sub(r"^```(?:json)?\s*", "", content.strip(), flags=re.IGNORECASE)
        content = re.sub(r"\s*```$", "", content.strip())


        try:
            parsed = self.output_type.model_validate_json(content)
        except Exception as e:
            print(f"⚠️ Parsing failed for {self.name}: {e}")
            raise e

        return type("AgentResult", (object,), {"final_output": parsed})


class Runner:
    @staticmethod
    async def run(agent, prompt):
        return await agent.run(prompt)