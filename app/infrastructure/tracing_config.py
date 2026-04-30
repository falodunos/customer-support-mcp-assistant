import os
from contextlib import contextmanager, nullcontext
from typing import Any, Iterator

try:
    from agents import custom_span, function_span, generation_span, trace
except ImportError:
    custom_span = None
    function_span = None
    generation_span = None
    trace = None


def tracing_enabled() -> bool:
    return os.getenv("OPENAI_TRACING_ENABLED", "true").lower() in {"true", "1", "yes"}


def _stringify_metadata(metadata: dict[str, Any] | None) -> dict[str, str]:
    if not metadata:
        return {}

    return {
        str(key): str(value)
        for key, value in metadata.items()
        if value is not None
    }


@contextmanager
def app_trace(
    workflow_name: str,
    group_id: str,
    metadata: dict[str, Any] | None = None,
) -> Iterator[None]:
    if not tracing_enabled() or trace is None:
        with nullcontext():
            yield
        return

    with trace(
        workflow_name=workflow_name,
        group_id=group_id,
        metadata=_stringify_metadata(metadata),
    ):
        yield


@contextmanager
def app_function_span(name: str, input_summary: str | None = None) -> Iterator[None]:
    if not tracing_enabled() or function_span is None:
        with nullcontext():
            yield
        return

    with function_span(name=name, input=input_summary):
        yield


@contextmanager
def app_generation_span(
    model: str,
    operation: str,
    input_summary: str | None = None,
) -> Iterator[None]:
    if not tracing_enabled() or generation_span is None:
        with nullcontext():
            yield
        return

    with generation_span(
        input=[{"role": "system", "content": input_summary or operation}],
        model=model,
        model_config={"operation": operation},
    ):
        yield


@contextmanager
def app_custom_span(name: str, data: dict[str, Any] | None = None) -> Iterator[None]:
    if not tracing_enabled() or custom_span is None:
        with nullcontext():
            yield
        return

    with custom_span(name=name, data=_stringify_metadata(data)):
        yield