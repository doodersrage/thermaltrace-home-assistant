"""Constants for the ThermalTrace integration."""

DOMAIN = "thermaltrace"

CONF_BASE_URL = "base_url"
CONF_SHARE_TOKEN = "share_token"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_INBOUND_TOKEN = "inbound_token"
CONF_INBOUND_SECRET = "inbound_secret"
CONF_INGEST_KEY = "ingest_key"

DEFAULT_BASE_URL = "https://thermaltrace.dev"
DEFAULT_SCAN_INTERVAL = 300

ATTR_DEVICE = "device"
ATTR_KIND = "kind"
ATTR_RECORDED_AT = "recorded_at"
ATTR_KEY = "key"

SERVICE_SNOOZE = "snooze"
SERVICE_VACATION = "vacation"
SERVICE_CLEAR_SNOOZE = "clear_snooze"
SERVICE_CLEAR_VACATION = "clear_vacation"
SERVICE_STATUS = "status"
SERVICE_PUSH = "push"
