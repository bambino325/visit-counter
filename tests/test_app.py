import redis

from app.main import create_app


class FakeRedis:
    """A simple Redis substitute for application tests, 
    so we dont have to rely on a real Redis server during testing."""

    def __init__(self):
        self.count = 0
        self.available = True

    def incr(self, key):
        assert key == "visits"
        self.count += 1
        return self.count

    def ping(self):
        if not self.available:
            raise redis.ConnectionError("Redis is unavailable")
        return True


def test_home_endpoint():
    fake_redis = FakeRedis()
    app = create_app(fake_redis)
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.json["message"] == "Hello DevOps"
    assert isinstance(response.json["hostname"], str)


def test_visits_increment():
    fake_redis = FakeRedis()
    app = create_app(fake_redis)
    client = app.test_client()

    response1 = client.get("/visits")
    response2 = client.get("/visits")
    response3 = client.get("/visits")

    assert response1.json == {"visits": 1}
    assert response2.json == {"visits": 2}
    assert response3.json == {"visits": 3}


def test_health_when_redis_is_available():
    fake_redis = FakeRedis()
    app = create_app(fake_redis)
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_health_when_redis_is_unavailable():
    fake_redis = FakeRedis()
    fake_redis.available = False

    app = create_app(fake_redis)
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json == {"status": "error"}
