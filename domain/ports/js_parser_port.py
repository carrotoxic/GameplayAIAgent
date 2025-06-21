from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class JSParserPort(ABC):
    """
    Hexagonal *outbound* port for parsing JavaScript code and responses.
    
    This port provides an interface for parsing JavaScript code
    and extracting structured data from JavaScript responses.
    """
    
    @abstractmethod
    def parse_js_response(self, js_response: str) -> Dict[str, Any]:
        """
        Parse a JavaScript response into structured data.
        
        Args:
            js_response: The JavaScript response to parse
            
        Returns:
            Dictionary containing parsed data
            
        Raises:
            ValueError: If the response cannot be parsed
        """
        ...
    
    @abstractmethod
    def extract_json_from_js(self, js_code: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON data from JavaScript code.
        
        Args:
            js_code: The JavaScript code to parse
            
        Returns:
            Extracted JSON data if found, None otherwise
        """
        ...
    
    @abstractmethod
    def parse_js_function_call(self, js_code: str) -> Dict[str, Any]:
        """
        Parse a JavaScript function call.
        
        Args:
            js_code: The JavaScript function call to parse
            
        Returns:
            Dictionary containing function name and arguments
            
        Raises:
            ValueError: If the function call cannot be parsed
        """
        ...
    
    @abstractmethod
    def validate_js_syntax(self, js_code: str) -> bool:
        """
        Validate JavaScript syntax.
        
        Args:
            js_code: The JavaScript code to validate
            
        Returns:
            True if syntax is valid, False otherwise
        """
        ...
    
    @abstractmethod
    def extract_js_variables(self, js_code: str) -> List[str]:
        """
        Extract variable names from JavaScript code.
        
        Args:
            js_code: The JavaScript code to parse
            
        Returns:
            List of variable names found in the code
        """
        ...
    
    @abstractmethod
    def parse_js_object(self, js_code: str) -> Dict[str, Any]:
        """
        Parse a JavaScript object literal.
        
        Args:
            js_code: The JavaScript object to parse
            
        Returns:
            Dictionary representation of the object
            
        Raises:
            ValueError: If the object cannot be parsed
        """
        ...
    
    @abstractmethod
    def extract_js_comments(self, js_code: str) -> List[str]:
        """
        Extract comments from JavaScript code.
        
        Args:
            js_code: The JavaScript code to parse
            
        Returns:
            List of comments found in the code
        """
        ...
    
    @abstractmethod
    def format_js_code(self, js_code: str) -> str:
        """
        Format JavaScript code for better readability.
        
        Args:
            js_code: The JavaScript code to format
            
        Returns:
            Formatted JavaScript code
        """
        ...
    
    @abstractmethod
    def minify_js_code(self, js_code: str) -> str:
        """
        Minify JavaScript code by removing unnecessary whitespace and comments.
        
        Args:
            js_code: The JavaScript code to minify
            
        Returns:
            Minified JavaScript code
        """
        ...
    
    @abstractmethod
    def extract_js_imports(self, js_code: str) -> List[str]:
        """
        Extract import statements from JavaScript code.
        
        Args:
            js_code: The JavaScript code to parse
            
        Returns:
            List of import statements found in the code
        """
        ...
