from __future__ import annotations
import re
from typing import Optional
from domain.ports.parser_port import ParserPort
from javascript import require
from domain.models import CodeSnippet

# Load JavaScript parser and code formatter
babel = require("@babel/core")
babel_generator = require("@babel/generator")

class JSParser(ParserPort):
    """
    Convert a LLM reply like:
    
        Code:
        ```javascript
        // code
        ```

    into AST and then convert the AST into a justified javascript code.
    and return a javascript code.
    """

    def parse(self, text: str) -> Optional[CodeSnippet]:
        # Extract the JavaScript code block
        match = re.search(r"```(?:javascript|js)(.*?)```", text, re.DOTALL)
        if not match:
            return None
        code_text = match.group(1).strip()
        if not code_text:
            return None

        # Basic checks for security or invalid pattern
        if 'async function' not in code_text or 'bot' not in code_text:
            return None
        if any(kw in code_text for kw in ["eval", "Function(", "while(true)"]):
            return None

        # Parse the code
        try:
            ast = babel.parse(code_text)
        except Exception as e:
            print(f"[JSParser] Babel parse error")
            return None
        functions = []
        for node in ast.program.body:
            if node.type != "FunctionDeclaration":
                continue
            is_async = getattr(node, "async", False)
            function_type = "AsyncFunctionDeclaration" if is_async else "FunctionDeclaration"
            try:
                function_code = babel_generator.generate(node)["code"]
            except Exception as e:
                print(f"[JSParser] Babel generate error")
                continue
            functions.append({
                "name": node.id.name,
                "type": function_type,
                "params": [param.name for param in node.params],
                "body": function_code
            })

        # Pick the last valid async function with bot parameter
        main_function = None
        for function in reversed(functions):
            if function["type"] == "AsyncFunctionDeclaration" and function["params"] == ["bot"]:
                main_function = function
                break

        if main_function is None:
            print("[JSParser] No valid async function(bot) found.")
            return None

        # Assemble final code parts
        main_function_code = "\n\n".join(f["body"] for f in functions)
        execution_code = f"await {main_function['name']}(bot);"

        return CodeSnippet(
            function_name=main_function["name"],
            main_function_code=main_function_code,
            execution_code=execution_code
        )

# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":
    parser = JSParser()
    text = """
    Code:
    ```javascript
    async function craftWoodenPickaxe(bot) {
    // Check if we already have the required items
    const hasOakLog = bot.inventory.has('oak_log');
    const hasWoodenPickaxe = bot.inventory.has('wooden_pickaxe');

    if (!hasOakLog || !hasWoodenPickaxe) {
        // We don't have the required items, collect them first
        await mineBlock(bot, 'oak_log', 1);
        await craftItem(bot, 'wooden_pickaxe', 1);
    }

    bot.chat("Crafting wooden pickaxe...");
    }
    ```
    """
    print(parser.parse(text))