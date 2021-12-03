import logging

from redis import StrictRedis
from rediscluster import RedisCluster


class RedisVanilla:
    def __init__(self, envmap):
        self.host = envmap["host"]
        self.port = int(envmap["port"])
        self.user = envmap["user"]
        self.password = envmap["pass"]
        if self.password == "":
            self.password = None
        self.cluster = bool(envmap["cluster"])
        if self.cluster:
            self.r = RedisCluster(
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                decode_responses=True,
            )
        else:
            self.r = StrictRedis(
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                decode_responses=True,
            )
        logging.info("RedisVanilla: pinging DB...")
        self.r.ping()

    def setup(self):
        logging.info("RedisVanilla: flushing DB to ensure a clean state")
        self.r.flushall()
