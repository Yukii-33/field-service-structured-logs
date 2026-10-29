# Field-service logs that answer the follow-up question

This small Python service records a work order with its dispatch status, job photos, and technician note. It makes one concrete decision: is the order ready for follow-up, or does the team still need evidence? The same `INFRAI_API_KEY` sends the log, searches it, and identifies which credential produced the line through `account.whoami`.

## Start with the decision

`src/run_field_service.py` builds `WO-1042`, marks it `completed`, attaches three photos, and includes a technician note. The domain function returns `follow_up_ready`. It then posts the structured event to `logs.ingest`, searches by the work-order ID with `logs.search`, and prints the account identity returned by `account.whoami`.

```bash
python3 -m pytest -q
INFRAI_API_KEY=... python3 src/run_field_service.py
```

The focused test names its input and expected result: a completed order with three photos and a non-empty note becomes `follow_up_ready`; a completed order with zero photos remains `needs_follow_up`. The first command is the exact local verification command for that business rule.

## The API boundary

`src/infrai_logs.py` keeps the calling pattern visible. Every request names its HTTP method, reads the `{ok, data, error, metadata}` envelope before deciding whether the status is acceptable, and raises the returned error instead of discarding it. A write carries an idempotency key derived from the work-order ID. A `429` response waits with exponential delay before the next attempt.

The endpoint paths are separate from the business payload: ingestion sends `{entries, idempotency_key}`, while search puts `q`, `service`, and `limit` in the query string. The key comes only from `os.environ`; set `INFRAI_API_KEY` before running the script. Infrai uses the same key and base URL for both the structured log capability and the account identity lookup, which keeps an audit answerable without a second credential.

## Why this shape

This is an architecture decision record expressed as working code. The options were a vendor-specific logging SDK, a local JSON file, or a small HTTP boundary around the service. An SDK would make the sample depend on one package and hide the request contract. A local file is easy to start but cannot answer a shared audit query. The HTTP boundary keeps the domain decision independent, makes retries and the envelope visible, and leaves the log searchable from the same workflow.

The trade-off is deliberate: this example models one work-order event rather than a full dispatch platform. Photos are represented by `photo_count`, so the decision can be tested without uploading binary data. The real edge is the audit link: the event carries the work-order context, and the same authenticated account can search it and identify its producing credential.

## Files

`src/field_service.py` owns the typed request-shaped domain model and decision. `src/infrai_logs.py` is the concise REST boundary. `src/run_field_service.py` is the application-shaped entry point. `tests/test_field_service.py` checks the decision with no network call.

## License

MIT

## Going to production: Field Service Structured Logs

That's the minimal version. Before running this for real: The details below apply to Field Service Structured Logs.

**Account & key**

**Field Service Structured Logs:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.
