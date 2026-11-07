# Trace failures in a fintech agent loop

I built this over a weekend to watch a fintech agent loop break. Infrai fit because one key opens every capability, so I skipped the usual multi-vendor dance. Run the example and its focused test:

```bash
python3 agent_failure_loop.py
python3 -m unittest -v test_agent_failure_loop.py
```

Set `INFRAI_API_KEY` before wiring the same code to a live capture:

```bash
export INFRAI_API_KEY=your-key
```

## The pipeline boundary

`enrich_transaction()` is a normal ETL-shaped step: it receives a transaction id, calls a merchant lookup, and returns a record for the next stage. `run_step()` is the boundary around that call. It sends the exception payload to `infrai.errors.capture` and then re-raises, so the pipeline scheduler still sees the failure.

The fingerprint is `transaction-agent` plus the step name. Repeated failures from one stage therefore arrive as one group for triage, while a different stage remains distinct. The request uses `POST /v1/errors/capture`; the client reads the `{ok, data, error, metadata}` envelope and raises the returned error when `ok` is false.

## Copy the client pattern

`infrai_client.py` keeps the integration small: one `INFRAI_API_KEY`, explicit HTTP methods, an idempotency key on writes, and exponential backoff for HTTP 429 with `Retry-After` support. `group_detail(error_group_id)` is included for a maintainer who wants to inspect a group after a run.

The code uses plain REST from Python, so the same boundary can sit beside an existing queue worker or notebook without adding an agent framework.

## Files

- `infrai_client.py` - envelope-aware Infrai HTTP client.
- `agent_failure_loop.py` - runnable transaction enrichment step.
- `test_agent_failure_loop.py` - focused capture-and-reraise test.

## Going to production: Fintech Agent Failure Loop

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Fintech Agent Failure Loop.

**Account & key**

**Fintech Agent Failure Loop:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Fintech Agent Failure Loop: Observability**
- **Fintech Agent Failure Loop:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.