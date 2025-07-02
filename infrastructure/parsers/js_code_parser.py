import re
from domain.models import CodeSnippet
from domain.ports import ParserPort

class JSParser(ParserPort):
    def parse(self, text: str) -> CodeSnippet:
        # Extract JavaScript code block
        match = re.search(r"```(?:javascript|js)?(.*?)```", text, re.DOTALL)
        code = match.group(1).strip() if match else text.strip()

        function_blocks = []
        lines = code.splitlines()
        in_func = False
        brace_depth = 0
        current_func = []
        func_name = None

        for line in lines:
            if not in_func:
                match = re.match(r'\s*async\s+function\s+(\w+)\s*\(\s*bot\s*\)\s*\{', line)
                if match:
                    in_func = True
                    brace_depth = 1
                    func_name = match.group(1)
                    current_func = [line]
            else:
                current_func.append(line)
                brace_depth += line.count('{')
                brace_depth -= line.count('}')
                if brace_depth == 0:
                    function_blocks.append((func_name, '\n'.join(current_func)))
                    in_func = False
                    current_func = []
                    func_name = None

        if not function_blocks:
            print("[JSParser] No valid async function(bot) found.")
            return CodeSnippet(function_name="unknown_function", main_function_code=code, execution_code=None)

        # Combine all function bodies
        main_function_code = "\n\n".join(body for _, body in function_blocks)
        main_function_name = function_blocks[-1][0]
        execution_code = f"await {main_function_name}(bot);"

        return CodeSnippet(
            function_name=main_function_name,
            main_function_code=main_function_code,
            execution_code=execution_code
        )

    def extract_plan(self, llm_response: str) -> str:
        match = re.search(
            r"Plan:\s*((?:.|\n)*?)(?=\n(?:Explain|Thought|Code):)",
            llm_response
        )
        return match.group(1) if match else ""


    def extract_thought(self, llm_response: str) -> str:
        match = re.search(
            r"Explain:\s*((?:.|\n)*?)(?=\n(?:Plan|Thought|Code):)",
            llm_response
        )
        return match.group(1).strip() if match else ""