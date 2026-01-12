"""Code Executor Tool for CrewAI agents.

WARNING: This tool executes arbitrary code. Only use in trusted environments.
"""

import io
import subprocess
import sys
from contextlib import redirect_stdout
from typing import Any, Dict, List, Optional, Type

import numpy as np
import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr


class CodeExecutorSchema(BaseModel):
    """Schema for code execution tool input."""

    code: str = Field(description="The Python code to execute.")
    required_libraries: Optional[List[str]] = Field(
        default=None,
        description="Python libraries to install via pip before execution.",
    )


class CodeExecutor(BaseTool):
    """Executes Python code in a shared namespace with library installation support."""

    name: str = "Code Executor"
    description: str = (
        "Executes Python code in a shared environment. "
        "Use print() to see results. Returns stdout/stderr."
    )
    args_schema: Type[BaseModel] = CodeExecutorSchema
    _execution_namespace: Dict[str, Any] = PrivateAttr(default_factory=dict)

    def __init__(self, namespace: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        self._execution_namespace = namespace if namespace else {}
        self._execution_namespace.setdefault("pd", pd)
        self._execution_namespace.setdefault("np", np)

    def _run(self, code: str, required_libraries: Optional[List[str]] = None) -> str:
        """Execute code after installing any required libraries."""
        result = []

        if required_libraries:
            result.append(self._install_libraries(required_libraries))

        result.append(self._execute_code(code))
        return "".join(result)

    def _install_libraries(self, libraries: List[str]) -> str:
        """Install libraries using pip."""
        log = "--- Installing Libraries ---\n"
        python_exe = sys.executable

        for lib in libraries:
            log += f"Installing {lib}...\n"
            try:
                process = subprocess.run(
                    [python_exe, "-m", "pip", "install", lib],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=120,
                )
                if process.returncode == 0:
                    log += f"Successfully installed {lib}\n"
                else:
                    log += f"Failed to install {lib} (code {process.returncode})\nError: {process.stderr}\n"
            except Exception as e:
                log += f"Error installing {lib}: {e}\n"

        log += "--- Installation Complete ---\n\n"
        return log

    def _execute_code(self, code: str) -> str:
        """Execute Python code in the shared namespace."""
        log = "--- Executing Code ---\n"
        output_buffer = io.StringIO()

        try:
            with redirect_stdout(output_buffer):
                exec(code, self._execution_namespace)

            output = output_buffer.getvalue()
            if output.strip():
                log += f"Code executed successfully.\n\nOutput:\n{output}\n"
            else:
                log += "Code executed successfully (no output).\n"
        except Exception as e:
            log += f"Execution error: {type(e).__name__}: {e}\n"
            partial = output_buffer.getvalue()
            if partial:
                log += f"\nPartial output:\n{partial}\n"

        return log


def create_code_executor(namespace: Optional[Dict[str, Any]] = None) -> CodeExecutor:
    """Factory function to create a CodeExecutor tool."""
    return CodeExecutor(namespace=namespace)


if __name__ == "__main__":
    print("Testing Code Executor Tool...")
    executor = create_code_executor(globals())

    test_code = """
x = 10
y = 20
print(f"Sum: {x + y}")
"""
    print(executor._run(test_code))
