import os
import json
from typing import Type, TypeVar
from pydantic import BaseModel
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.core.logging import logger
from app.models.schemas import (
    QueryAnalysisOutput,
    DocumentGradingOutput,
    ChunkEvaluation,
    QueryRewriteOutput,
    AnswerValidationOutput,
)

T = TypeVar("T", bound=BaseModel)


class MockChatModel:
    """Mock LLM for deterministic testing or when no API key is provided."""

    def invoke(self, messages, **kwargs):
        content = ""
        if isinstance(messages, list):
            content = " ".join([m.content for m in messages if hasattr(m, "content")])
        else:
            content = str(messages)

        return HumanMessage(content="This is a mock LLM response based on retrieved documentation.")

    def with_structured_output(self, schema: Type[T]):
        class MockStructuredRunnable:
            def __init__(self, schema_cls: Type[T]):
                self.schema_cls = schema_cls

            def invoke(self, messages, **kwargs):
                prompt_str = ""
                if isinstance(messages, list):
                    prompt_str = " ".join([getattr(m, "content", str(m)) for m in messages])
                else:
                    prompt_str = str(messages)

                if self.schema_cls == QueryAnalysisOutput:
                    # Detect intent from prompt
                    lower = prompt_str.lower()
                    query_type = "conceptual"
                    if "how" in lower or "step" in lower:
                        query_type = "how_to"
                    elif "error" in lower or "fix" in lower or "trouble" in lower:
                        query_type = "troubleshooting"
                    elif "api" in lower or "param" in lower:
                        query_type = "api_reference"

                    return QueryAnalysisOutput(
                        query_type=query_type,
                        technical_keywords=["fastapi", "dependency", "injection", "request", "route"],
                        is_ambiguous=False,
                        optimized_query=prompt_str[:100],
                    )

                elif self.schema_cls == DocumentGradingOutput:
                    # Grade chunks based on presence in prompt
                    evaluations = []
                    # Try to extract chunk_ids from prompt
                    import re
                    chunk_ids = re.findall(r"Chunk ID:\s*([^\s\n]+)", prompt_str)
                    if not chunk_ids:
                        chunk_ids = ["chunk_0", "chunk_1"]
                    
                    for idx, cid in enumerate(chunk_ids):
                        evaluations.append(
                            ChunkEvaluation(
                                chunk_id=cid,
                                classification="relevant" if idx == 0 or "fastapi" in prompt_str.lower() else "irrelevant",
                                relevance_score=0.95 if idx == 0 else 0.1,
                                reason="Matches core technical concepts in query" if idx == 0 else "Off-topic chunk"
                            )
                        )
                    return DocumentGradingOutput(evaluations=evaluations)

                elif self.schema_cls == QueryRewriteOutput:
                    return QueryRewriteOutput(
                        rewritten_query=f"{prompt_str[:80]} alternative terms dependency injection parameters architecture",
                        explanation="Expanded technical query with synonyms"
                    )

                elif self.schema_cls == AnswerValidationOutput:
                    return AnswerValidationOutput(
                        groundedness_classification="supported",
                        groundedness_score=0.90,
                        unsupported_claims=[]
                    )

                raise ValueError(f"Unsupported mock schema: {self.schema_cls}")

        return MockStructuredRunnable(schema)


class LLMService:
    """LLM Provider Manager supporting Gemini, OpenAI, and Mock fallback."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.llm = self._init_llm()

    def _init_llm(self):
        if self.provider == "gemini" and settings.GEMINI_API_KEY:
            logger.info("Initializing Google Gemini Flash LLM...")
            try:
                return ChatGoogleGenerativeAI(
                    model=settings.LLM_MODEL,
                    google_api_key=settings.GEMINI_API_KEY,
                    temperature=settings.LLM_TEMPERATURE,
                    convert_system_message_to_human=True,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini ({e}). Falling back to Mock LLM.")
                return MockChatModel()
        else:
            logger.info("Using Mock LLM Service (Provider=mock or API Key missing).")
            return MockChatModel()

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Executes a standard LLM completion."""
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        response = self.llm.invoke(messages)
        return response.content

    def generate_structured(self, prompt: str, schema: Type[T], system_prompt: str = "") -> T:
        """Generates structured output validated against a Pydantic schema."""
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        try:
            structured_llm = self.llm.with_structured_output(schema)
            return structured_llm.invoke(messages)
        except Exception as e:
            logger.warning(f"Structured output call failed ({e}). Falling back to json repair parser.")
            # Fallback for LLMs that don't directly support with_structured_output
            raw_text = self.generate(
                prompt + f"\n\nRespond ONLY with valid JSON matching this schema:\n{schema.model_json_schema()}",
                system_prompt
            )
            # Find json block
            start = raw_text.find("{")
            end = raw_text.rfind("}")
            if start != -1 and end != -1:
                json_str = raw_text[start:end+1]
                return schema.model_validate_json(json_str)
            raise e


llm_service = LLMService()
