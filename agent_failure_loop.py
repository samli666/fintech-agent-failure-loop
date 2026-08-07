"""Capture failures from a small transaction-enrichment agent loop."""
import traceback
from typing import Callable, Any

from infrai_client import infrai

# The equivalent SDK-style idiom is infrai.errors.capture.


def run_step(step: str, fn: Callable[..., Any], **inputs: Any) -> Any:
    try:
        return fn(**inputs)
    except Exception as exc:
        infrai.capture(
            title=f"transaction-agent/{step} failed",
            message=f"{type(exc).__name__}: {exc}",
            level="error",
            fingerprint=["transaction-agent", step],
            exception=traceback.format_exc(),
            context={"step": step, "inputs": inputs},
        )
        raise


def enrich_transaction(transaction_id: str, lookup: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    """Run one pipeline step and preserve the original exception for callers."""
    return run_step("merchant-lookup", lookup, transaction_id=transaction_id)


if __name__ == "__main__":
    def lookup(**_: Any) -> dict[str, Any]:
        return {"merchant": "northwind-books", "category": "books"}

    result = enrich_transaction("txn-1042", lookup)
    print(result)
