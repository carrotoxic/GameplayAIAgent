from __future__ import annotations
import re
from typing import Any
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

    def parse(self, text: str) -> CodeSnippet:
        # extract the code pattern using regex from the text
        code_pattern = re.compile(r"```(?:javascript|js)(.*?)```", re.DOTALL)
        code_text = "\n".join(code_pattern.findall(text))
        if not code_text.strip():
            return None
        
        # parse the code text into a AST
        code_ast = babel.parse(code_text)
        function_name = code_ast.program.body[0].id.name
        # format the AST into a javascript code
        formatted_code = babel_generator.generate(code_ast)["code"]

        return CodeSnippet(
            function_name=function_name,
            code=formatted_code
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