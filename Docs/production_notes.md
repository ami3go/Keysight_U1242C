# Production Notes

- Use realistic timeouts. A 100 ms serial timeout is too aggressive for unattended operation.
- Keep `auto_reconnect=True` for long tests.
- Use structured logging from Python's `logging` module.
- Side-effect commands are not blindly retried by default.
- Keep hardware smoke tests separate from normal unit tests.
- Use CSV logs with an error column to preserve failed-sample visibility.
- Do not decode `STAT?` bits until the official mapping is available; preserve raw status.
