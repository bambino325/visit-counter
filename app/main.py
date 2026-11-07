import logging
import os
import socket
import sys

import redis
from flask import Flask, jsonify, request


logger = logging.getLogger("visit_counter")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.propagate = False


def create_app(redis_client=None):
    app = Flask(__name__)

    if redis_client is None:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            decode_responses=True
        )

    @app.get("/")
    def home():
        return jsonify({
            "message": "Hello DevOps",
            "hostname": socket.gethostname()
        })

    # incr() atomically increments the value of the key "visits" in Redis and returns the new value, if key exists, 
    # otherwise it initializes the key with a value of 1 and returns 1.
    @app.get("/visits")
    def visits():
        count = redis_client.incr("visits")
        return jsonify({"visits": count})

    @app.get("/health")
    def health():
        try:
            redis_client.ping()
            return jsonify({"status": "ok"}), 200
        except redis.RedisError:
            return jsonify({"status": "error"}), 503

    @app.after_request
    def log_request(response):
        logger.info(
            "%s %s %s",
            request.method,
            request.path,
            response.status_code
        )
        return response

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
