"""Ollama HTTP client — owns translation to/from Ollama API."""

from __future__ import annotations

import json
import socket
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Iterator

from hypermind.models import ModelRequest, ProviderError

HttpHandler = Callable[[str, str, bytes | None, float], tuple[int, dict[str, Any]]]
StreamHandler = Callable[[str, str, bytes | None, float], Iterator[dict[str, Any]]]


def default_http(
    method: str, url: str, body: bytes | None, timeout: float
) -> tuple[int, dict[str, Any]]:
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            if not raw:
                return resp.status, {}
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ProviderError("ollama", "malformed_response", str(exc)) from exc
    except ProviderError:
        raise
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ProviderError(
            "ollama", "http_error", f"HTTP {exc.code}: {detail[:300]}"
        ) from exc
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        if isinstance(reason, socket.timeout) or "timed out" in str(reason).lower():
            raise ProviderError("ollama", "timeout", "request timed out") from exc
        raise ProviderError("ollama", "connection_failed", str(reason)) from exc
    except (TimeoutError, socket.timeout) as exc:
        raise ProviderError("ollama", "timeout", "request timed out") from exc


def default_http_stream(
    method: str, url: str, body: bytes | None, timeout: float
) -> Iterator[dict[str, Any]]:
    """NDJSON stream reader for Ollama `stream: true` responses."""
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json", "Accept": "application/x-ndjson"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ProviderError(
            "ollama", "http_error", f"HTTP {exc.code}: {detail[:300]}"
        ) from exc
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        if isinstance(reason, socket.timeout) or "timed out" in str(reason).lower():
            raise ProviderError("ollama", "timeout", "request timed out") from exc
        raise ProviderError("ollama", "connection_failed", str(reason)) from exc
    except (TimeoutError, socket.timeout) as exc:
        raise ProviderError("ollama", "timeout", "request timed out") from exc

    try:
        while True:
            line = resp.readline()
            if not line:
                break
            text = line.decode("utf-8").strip()
            if not text:
                continue
            try:
                yield json.loads(text)
            except json.JSONDecodeError as exc:
                raise ProviderError("ollama", "malformed_response", str(exc)) from exc
    finally:
        resp.close()


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 45.0,
        *,
        probe_timeout_seconds: float = 3.0,
        first_token_timeout_seconds: float = 25.0,
        keep_alive: str | None = "10m",
        http: HttpHandler | None = None,
        http_stream: StreamHandler | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.probe_timeout_seconds = probe_timeout_seconds
        self.first_token_timeout_seconds = first_token_timeout_seconds
        self.keep_alive = keep_alive
        self._http = http or default_http
        self._http_stream = http_stream or default_http_stream

    def list_tags(self) -> list[str]:
        status, data = self._http(
            "GET",
            f"{self.base_url}/api/tags",
            None,
            self.probe_timeout_seconds,
        )
        if status >= 400:
            raise ProviderError("ollama", "http_error", f"tags status {status}")
        models = data.get("models") or []
        names: list[str] = []
        for item in models:
            name = item.get("name") if isinstance(item, dict) else None
            if name:
                names.append(str(name))
        return names

    def _messages(self, request: ModelRequest) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if request.system:
            messages.append({"role": "system", "content": request.system})

        user_content = request.prompt
        if request.context:
            ctx = "\n\n".join(request.context)
            if not ctx.lstrip().startswith("[CONTEXT]"):
                ctx = f"Bounded context (use only what is relevant):\n{ctx}"
            user_content = f"{ctx}\n\nUSER REQUEST:\n{request.prompt}"
        messages.append({"role": "user", "content": user_content})
        return messages

    def _payload(
        self,
        model: str,
        request: ModelRequest,
        *,
        stream: bool,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": self._messages(request),
            "stream": stream,
        }
        if self.keep_alive is not None:
            payload["keep_alive"] = self.keep_alive
        options: dict[str, Any] = {}
        if request.temperature is not None:
            options["temperature"] = request.temperature
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        if options:
            payload["options"] = options
        return payload

    def chat(
        self,
        model: str,
        request: ModelRequest,
        *,
        stream: bool = False,
        timeout_seconds: float | None = None,
        on_token: Callable[[str], None] | None = None,
        first_token_timeout_seconds: float | None = None,
    ) -> str:
        timeout = float(
            timeout_seconds
            if timeout_seconds is not None
            else self.timeout_seconds
        )
        if stream or on_token is not None:
            return self._chat_stream(
                model,
                request,
                timeout=timeout,
                on_token=on_token,
                first_token_timeout_seconds=first_token_timeout_seconds,
            )

        body = json.dumps(self._payload(model, request, stream=False)).encode("utf-8")
        status, data = self._http(
            "POST", f"{self.base_url}/api/chat", body, timeout
        )
        if status >= 400:
            raise ProviderError("ollama", "http_error", f"chat status {status}")

        message = data.get("message")
        if not isinstance(message, dict):
            raise ProviderError(
                "ollama", "malformed_response", "missing message object"
            )
        content = message.get("content")
        if not isinstance(content, str):
            raise ProviderError(
                "ollama", "malformed_response", "missing message.content"
            )
        return content

    def _chat_stream(
        self,
        model: str,
        request: ModelRequest,
        *,
        timeout: float,
        on_token: Callable[[str], None] | None,
        first_token_timeout_seconds: float | None,
    ) -> str:
        body = json.dumps(self._payload(model, request, stream=True)).encode("utf-8")
        first_limit = float(
            first_token_timeout_seconds
            if first_token_timeout_seconds is not None
            else self.first_token_timeout_seconds
        )
        # Fail-fast: socket stalls should not exceed first-token budget.
        stream_timeout = min(timeout, first_limit) if first_limit > 0 else timeout
        started = time.perf_counter()
        saw_token = False
        parts: list[str] = []
        try:
            for chunk in self._http_stream(
                "POST", f"{self.base_url}/api/chat", body, stream_timeout
            ):
                if not saw_token and (time.perf_counter() - started) > first_limit:
                    raise ProviderError(
                        "ollama",
                        "first_token_timeout",
                        f"no tokens within {first_limit:.0f}s",
                    )
                message = chunk.get("message") if isinstance(chunk, dict) else None
                piece = ""
                if isinstance(message, dict) and isinstance(message.get("content"), str):
                    piece = message["content"]
                elif isinstance(chunk.get("response"), str):
                    piece = chunk["response"]
                if piece:
                    saw_token = True
                    parts.append(piece)
                    if on_token is not None:
                        on_token(piece)
                if chunk.get("done") is True:
                    break
        except ProviderError:
            raise
        except (TimeoutError, socket.timeout) as exc:
            code = "first_token_timeout" if not saw_token else "timeout"
            raise ProviderError(
                "ollama",
                code,
                "request timed out"
                if saw_token
                else f"no tokens within {first_limit:.0f}s",
            ) from exc

        text = "".join(parts)
        if not text and not saw_token:
            raise ProviderError(
                "ollama",
                "first_token_timeout",
                f"no tokens within {first_limit:.0f}s",
            )
        return text
