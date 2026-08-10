"""HyperMind intelligence routing + context engine + bounded local execution.

Provider-neutral orchestration: intent → agent → ContextPack → model → (optional) one generate → trace.
No autonomous execution loops. Cursor is not part of the runtime.
"""

__version__ = "0.3.0"