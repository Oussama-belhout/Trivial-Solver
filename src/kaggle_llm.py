"""Custom LangChain ChatModel that calls the Kaggle GPU inference server."""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Iterator, List, Optional

import requests
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field, model_validator


class KaggleChatModel(BaseChatModel):
    """LangChain ChatModel that delegates inference to a remote Kaggle notebook
    running a Flask API with a local GPU-loaded model (Gemma-2 9B IT).
    
    The server is expected to expose:
        POST /generate  — accepts {messages, temperature, max_tokens, json_mode}
        GET  /health    — returns model info
    """

    base_url: str = Field(default="", description="Base URL of the Kaggle inference server (ngrok)")
    temperature: float = Field(default=0.1, description="Sampling temperature")
    max_tokens: int = Field(default=4096, description="Maximum tokens to generate")
    max_retries: int = Field(default=3, description="Number of retries on connection errors")
    timeout: int = Field(default=180, description="Request timeout in seconds")
    model_name: str = Field(default="kaggle-qwen2.5-coder-7b-instruct", description="Model identifier for tracing")

    @model_validator(mode="after")
    def _resolve_base_url(self) -> "KaggleChatModel":
        if not self.base_url:
            self.base_url = os.getenv("KAGGLE_INFERENCE_URL", "")
        # Strip trailing slash
        self.base_url = self.base_url.rstrip("/")
        return self

    @property
    def _llm_type(self) -> str:
        return "kaggle-gemma"

    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    def _convert_messages(self, messages: List[BaseMessage]) -> list[dict]:
        """Convert LangChain messages to the server's expected format."""
        converted = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                converted.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                converted.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                converted.append({"role": "assistant", "content": msg.content})
            else:
                # Fallback — treat as user
                converted.append({"role": "user", "content": msg.content})
        return converted

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Call the Kaggle inference server."""
        if not self.base_url:
            raise ValueError(
                "KAGGLE_INFERENCE_URL is not set. Start the Kaggle notebook "
                "and paste the ngrok URL into your .env file."
            )

        payload = {
            "messages": self._convert_messages(messages),
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "json_mode": kwargs.get("json_mode", False),
        }

        # Retry loop for transient network errors
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/generate",
                    json=payload,
                    timeout=self.timeout,
                    headers={"ngrok-skip-browser-warning": "true"},
                )

                if response.status_code != 200:
                    error_body = response.text[:500]
                    raise ValueError(f"Kaggle server returned {response.status_code}: {error_body}")

                result = response.json()
                content = result.get("content", "")

                message = AIMessage(content=content)
                generation = ChatGeneration(message=message)
                return ChatResult(generations=[generation])

            except requests.exceptions.ConnectionError as e:
                last_error = e
                delay = 5 * (attempt + 1)
                print(f"    ⏳ Kaggle server connection error (attempt {attempt + 1}/{self.max_retries}), retrying in {delay}s...")
                time.sleep(delay)
            except requests.exceptions.Timeout as e:
                last_error = e
                delay = 5 * (attempt + 1)
                print(f"    ⏳ Kaggle server timeout (attempt {attempt + 1}/{self.max_retries}), retrying in {delay}s...")
                time.sleep(delay)

        raise ConnectionError(
            f"Failed to connect to Kaggle inference server at {self.base_url} "
            f"after {self.max_retries} attempts. Last error: {last_error}"
        )

    def with_structured_output(self, schema, **kwargs):
        """Return a wrapper that forces JSON output matching the given Pydantic schema."""
        return _KaggleStructuredOutput(llm=self, schema=schema)


class _KaggleStructuredOutput:
    """Wrapper that injects JSON-mode instructions into the prompt and parses
    the response into a Pydantic model.
    """

    def __init__(self, llm: KaggleChatModel, schema):
        self.llm = llm
        self.schema = schema  # Pydantic model class
        self._schema_json = json.dumps(schema.model_json_schema(), indent=2)

    def invoke(self, messages: List[BaseMessage], **kwargs) -> Any:
        """Invoke with JSON-mode prompt injection."""
        # Inject schema instructions into the system message
        schema_instruction = (
            f"\n\nYou MUST respond with ONLY a valid JSON object matching this exact schema:\n"
            f"```json\n{self._schema_json}\n```\n"
            f"Do NOT include any text outside the JSON object. "
            f"Do NOT wrap it in markdown code fences. "
            f"Start your response with {{ and end with }}."
        )

        # Find and augment the system message, or prepend one
        augmented = []
        has_system = False
        for msg in messages:
            if isinstance(msg, SystemMessage) and not has_system:
                augmented.append(SystemMessage(content=msg.content + schema_instruction))
                has_system = True
            else:
                augmented.append(msg)
        
        if not has_system:
            augmented.insert(0, SystemMessage(content=schema_instruction))

        # Call with json_mode flag
        result = self.llm._generate(augmented, json_mode=True)
        content = result.generations[0].message.content

        # Parse JSON from response
        content = content.strip()
        
        # Try to extract JSON if wrapped in code fences
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1).strip()
        
        # Try to find a JSON object
        json_obj_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_obj_match:
            content = json_obj_match.group(0)

        try:
            data = json.loads(content)
            return self.schema(**data)
        except (json.JSONDecodeError, Exception) as e:
            # If parsing fails, try a more aggressive extraction
            # Sometimes the model outputs extra text around the JSON
            try:
                # Find the outermost { ... }
                brace_count = 0
                start = content.index('{')
                for i, ch in enumerate(content[start:], start):
                    if ch == '{':
                        brace_count += 1
                    elif ch == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_str = content[start:i+1]
                            data = json.loads(json_str)
                            return self.schema(**data)
            except Exception:
                pass
            
            raise ValueError(
                f"Failed to parse Kaggle model response as {self.schema.__name__}.\n"
                f"Raw response:\n{content[:500]}\n"
                f"Parse error: {e}"
            )
