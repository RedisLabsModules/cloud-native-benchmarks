import csv
import logging

import redis


def execute_redis_init_commands(benchmark_config, r, dbconfig_keyname="dbconfig"):
    cmds = None
    if dbconfig_keyname in benchmark_config:
        if "init_commands" in benchmark_config[dbconfig_keyname]:
            cmds = benchmark_config[dbconfig_keyname]["init_commands"]
    if cmds is not None:
        for cmd in cmds:
            is_array = False
            if '"' in cmd:
                cols = []
                for lines in csv.reader(
                    cmd,
                    quotechar='"',
                    delimiter=" ",
                    quoting=csv.QUOTE_ALL,
                    skipinitialspace=True,
                ):
                    if lines[0] != " " and len(lines[0]) > 0:
                        cols.append(lines[0])
                cmd = cols
                is_array = True
            try:
                logging.info("Sending init command: {}".format(cmd))
                if is_array:
                    stdout = r.execute_command(*cmd)
                else:
                    stdout = r.execute_command(cmd)
                logging.info("Command reply: {}".format(stdout))
            except redis.connection.ConnectionError as e:
                logging.error(
                    "Error establishing connection to Redis. Message: {}".format(
                        e.__str__()
                    )
                )
