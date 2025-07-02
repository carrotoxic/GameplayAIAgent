from dataclasses import dataclass
from typing import Optional

@dataclass
class CodeSnippet:
    function_name: str
    main_function_code: str
    execution_code: Optional[str]

    def __str__(self):
        return f"function_name={self.function_name}\nmain_function_code={self.main_function_code}\nexecution_code={self.execution_code}"

# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":
    code_snippet = CodeSnippet(
        function_name="testMoveAgent",
        main_function_code="""
        async function testMoveAgent(bot) {
            bot.chat("Movement test finished.");
        }""",
        execution_code="await testMoveAgent(bot);"
    )
    print(code_snippet)