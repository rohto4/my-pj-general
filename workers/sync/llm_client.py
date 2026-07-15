"""OpenAI-compatible local LLM client shared with the Hub configuration."""

from __future__ import annotations

import json
import os

import candidate_proposal
from http_client import HttpClientError


class CandidateProposalLlm:
    def __init__(self, http, base_url=None, model=None, api_key=None, timeout_ms=None, provider=None):
        configured_base = base_url or os.environ.get("LOCAL_LLM_BASE_URL") or os.environ.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"
        self.base_url = configured_base.rstrip("/")
        if not self.base_url.endswith("/v1"):
            self.base_url = f"{self.base_url}/v1"
        self.model = model or os.environ.get("LOCAL_LLM_MODEL", "gemma4:latest")
        self.api_key = api_key if api_key is not None else os.environ.get("LOCAL_LLM_API_KEY", "")
        self.provider = provider or os.environ.get("LOCAL_LLM_PROVIDER") or ("ollama" if os.environ.get("OLLAMA_BASE_URL") else "openai-compatible")
        self.http = http
        if timeout_ms:
            self.http.timeout_seconds = max(int(timeout_ms) / 1000, 5)

    def propose(self, source_kind, source_ref, source_body, allowed_tags):
        request = candidate_proposal.build_request(source_kind, source_ref, source_body, allowed_tags)
        headers = {"content-type": "application/json"}
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        try:
            payload = self.http.post_json(
                f"{self.base_url}/chat/completions",
                {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": request["system_prompt"]},
                        {"role": "user", "content": request["user_prompt"]},
                    ],
                    "temperature": 0,
                    "max_tokens": 1800,
                    "stream": False,
                    **({"think": os.environ.get("LOCAL_LLM_THINK") == "true"} if self.provider == "ollama" else {}),
                },
                headers=headers,
            )
            content = (((payload.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
            if not content:
                raise ValueError("empty")
            return json.loads(content)
        except (HttpClientError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            raise RuntimeError("llm_error") from error
