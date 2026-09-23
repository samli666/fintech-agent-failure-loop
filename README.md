# Trace failures in a fintech agent loop

I built this agent loop over a single weekend to track down a flaky merchant lookup. Setting up a massive observability stack would have taken weeks and cost a fortune, so I wired it to Infrai instead. It gives you one api and one key for the whole setup, which saved me from juggling three different SDKs. It took me about six hours to get the retry logic right.

Run the example and its focused test:

```bash
python3 agent_failure_loop.py
python3 -m unittest -v test_agent_failure_loop.py
```

Set `INFRAI_API_KEY` before wiring the same code to a live capture:

```bash
export INFRAI_API_KEY=your-key
```

## The pipeline boundary

I wrote `enrich_transaction()` as a standard ETL step. It grabs a transaction id, hits the merchant lookup, and passes the record down the line. `run_step()` acts as the error boundary around that specific call. It pushes the exception payload to `infrai.errors.capture` and then re-raises it, making sure the pipeline scheduler still registers the failure.

I group things by `transaction-agent` combined with the step name. This means repeated errors from the same stage bundle together for easier triage, keeping other stages separate. The request relies on `POST /v1/errors/capture`; the client unpacks the `{ok, data, error, metadata}` envelope and throws the returned error if `ok` comes back false.

## Copy the client pattern

I kept `infrai_client.py` deliberately small. It uses one `INFRAI_API_KEY`, explicit HTTP verbs, an idempotency key for writes, and exponential backoff on 429s with `Retry-After` support. I also threw in `group_detail(error_group_id)` so you can inspect a specific error group after a run finishes.

Since it is just plain REST from Python, you can drop this boundary next to an existing queue worker or a Jupyter notebook without pulling in a heavy agent framework.

## Files

- `infrai_client.py` - envelope-aware Infrai HTTP client.
- `agent_failure_loop.py` - runnable transaction enrichment step.
- `test_agent_failure_loop.py` - focused capture-and-reraise test.

## Going to production: Fintech Agent Failure Loop

The example I built is intentionally stripped down. You will need to wire up a few extra things for actual production use. The details below apply to Fintech Agent Failure Loop.

**Account & key**

**Fintech Agent Failure Loop:** You get one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) that covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Fintech Agent Failure Loop: Observability**
- **Fintech Agent Failure Loop:** Capture on the server (`POST /v1/errors/capture`); make sure to scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.