"""Notebook Code Executor tool for CrewAI agents."""

import io
import subprocess
import sys
from contextlib import redirect_stdout
from typing import Any, Dict, List, Optional, Type

import numpy as np
import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr


class NotebookCodeExecutorSchema(BaseModel):
    """Schema for NotebookCodeExecutor tool input."""

    code: str = Field(description="The Python code to execute.")
    required_libraries: Optional[List[str]] = Field(
        default=None,
        description="Python libraries to install via pip before execution. Example: ['seaborn', 'pandas']",
    )


class NotebookCodeExecutor(BaseTool):
    """Executes Python code in a shared namespace and installs required libraries."""

    name: str = "Notebook Code Executor"
    description: str = (
        "Executes Python code in a shared namespace and installs required libraries. "
        "Use print() statements to see results. Returns stdout/stderr."
    )
    args_schema: Type[BaseModel] = NotebookCodeExecutorSchema
    _execution_namespace: Dict[str, Any] = PrivateAttr(default_factory=dict)

    def __init__(self, namespace: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        if namespace is not None:
            self._execution_namespace = namespace
            self._execution_namespace.setdefault("pd", pd)
            self._execution_namespace.setdefault("np", np)

    def _run(self, code: str, required_libraries: Optional[List[str]] = None) -> str:
        """Execute code in the configured namespace after installing any required libraries."""
        result_parts = []

        if required_libraries:
            result_parts.append(self._install_libraries(required_libraries))

        result_parts.append(self._execute_code(code))
        return "".join(result_parts)

    def _install_libraries(self, libraries: List[str]) -> str:
        """Install required libraries using pip."""
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
                    log += f"Successfully installed {lib}.\n"
                else:
                    log += f"Failed to install {lib}. Code: {process.returncode}\nStderr: {process.stderr}\n"
            except Exception as e:
                log += f"Error installing {lib}: {e}\n"

        log += "--- Library Installation Finished ---\n\n"
        return log

    def _execute_code(self, code: str) -> str:
        """Execute Python code in the shared namespace."""
        log = "--- Executing Code ---\n"
        output_buffer = io.StringIO()

        try:
            with redirect_stdout(output_buffer):
                exec(code, self._execution_namespace)

            output = output_buffer.getvalue() or "[No Print Output]"
            log += f"Code executed successfully. Output:\n```output\n{output}\n```\n"
        except Exception as e:
            error_msg = f"Error executing code: {type(e).__name__}: {e}\n"
            partial_output = output_buffer.getvalue()
            if partial_output:
                error_msg += f"Captured output before error:\n```output\n{partial_output}\n```\n"
            log += error_msg

        return log
