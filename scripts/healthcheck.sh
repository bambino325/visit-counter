#!/usr/bin/env bash

URL="$1"
MAX_ATTEMPTS=5
RETRY_INTERVAL=3

if [[ -z "$URL" ]]; then
    echo "Usage: $0 <URL>"
    exit 1
fi

for ((attempt = 1; attempt <= MAX_ATTEMPTS; attempt++)); do

    STATUS=$(curl -sS -o /dev/null -w "%{http_code}" \
        --max-time 2 "$URL" 2>/dev/null) || STATUS="000"

    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[$TIMESTAMP] Attempt $attempt/$MAX_ATTEMPTS - HTTP status: $STATUS"

    if [[ "$STATUS" =~ ^2[0-9]{2}$ ]]; then
        echo "Healthcheck successful!"
        exit 0
    fi

    if [[ "$attempt" -lt "$MAX_ATTEMPTS" ]]; then
        sleep "$RETRY_INTERVAL"
    fi
done

echo "Healthcheck failed after $MAX_ATTEMPTS attempts."
exit 1
