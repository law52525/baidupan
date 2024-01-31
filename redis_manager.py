import redis


class RedisManager:
    """ 全局redis控制器 """
    _redis_host = None
    _redis_port = None
    _password = None
    _instance = None

    @classmethod
    def init_config(cls, redis_host, redis_port, password=None):
        cls._redis_host = redis_host
        cls._redis_port = redis_port
        cls._password = password

    @classmethod
    def get_instance(cls):
        if not cls._redis_host or not cls._redis_port:
            raise Exception("Config not initialized")

        if not cls._instance:
            cls._instance = RedisInstance(
                cls._redis_host, cls._redis_port, cls._password)

        return cls._instance


class RedisInstance:
    """ redis实例 """

    def __init__(self, redis_host, redis_port, password=None):
        pool = redis.ConnectionPool(host=redis_host, port=redis_port,
                                    decode_responses=True, password=password)
        self.r = redis.Redis(connection_pool=pool, health_check_interval=30)

    def get(self, key):
        if isinstance(key, list):
            return self.r.mget(key)
        return self.r.get(key)

    def set(self, key, value, ex=None):
        self.r.set(key, value, ex=ex)

    def delete(self, key):
        self.r.delete(key)

    def hget(self, key, dict_key):
        return self.r.hget(key, dict_key)

    def hset(self, key, dict_key, value):
        self.r.hset(key, dict_key, value)

    def expire(self, key, expire_seconds=None):
        if expire_seconds:
            self.r.expire(key, expire_seconds)
