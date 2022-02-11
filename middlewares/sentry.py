from sentry_sdk.integrations.asgi import SentryAsgiMiddleware as SentryMiddleware
import sentry_sdk
import config

sentry_sdk.init(
    config.SENTRY_DSN,
    traces_sample_rate=1.0
)
