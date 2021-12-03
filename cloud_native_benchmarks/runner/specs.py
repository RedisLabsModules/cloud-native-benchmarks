#  Apache License Version 2.0
#
#  Copyright (c) 2021., Redis Performance Group
#  All rights reserved.
#
import json
import logging
import os
import pathlib

import yaml

from cloud_native_benchmarks.dbwrappers.RedisVanilla import RedisVanilla
from cloud_native_benchmarks.inventory.config import merge_default_inventory_spec


def retrieve_env_map(final_spec):
    env_map = {}
    result = True
    if "db" in final_spec:
        if "env" in final_spec["db"]:
            for env_var in final_spec["db"]["env"]:
                env_value = os.getenv(env_var, None)
                if env_value is None:
                    logging.error(
                        "Required environment var {} is None.".format(env_var)
                    )
                    result = False
                env_map[env_var] = env_value

    return result, env_map


def get_benchmark_specs(testsuites_folder, defaults_filename):
    files = pathlib.Path(testsuites_folder).glob("*.yml")
    files = [str(x) for x in files]
    specs = {}
    default_config = None
    for filename in files:
        if filename.endswith(defaults_filename):
            logging.info("Detected defaults filename: {}".format(defaults_filename))
            files.remove(filename)
            with open(filename, "r") as yml_file:
                default_config = yaml.safe_load(yml_file)
    logging.info(
        "Detected the following benchmark configs: \n\t{}".format(
            "\n\t".join([str(x) for x in files])
        )
    )

    result = True
    for filename in files:
        with open(filename, "r") as yml_file:
            benchmark_config = yaml.safe_load(yml_file)
            spec_result, final_spec = merge_default_inventory_spec(
                benchmark_config, default_config
            )

            if spec_result is True:
                specs[filename] = {}
                specs[filename]["test_name"] = benchmark_config["name"]

                specs[filename]["protocol"] = benchmark_config["protocol"]
                specs[filename]["inventory"] = final_spec

                specs[filename]["benchmark_config"] = benchmark_config
                result_env_map, env_map = retrieve_env_map(final_spec)
                if result_env_map is False:
                    result = False
                clientconfig = benchmark_config["clientconfig"]
                clientconfig_str = json.dumps(clientconfig)
                dbinit_str = final_spec["db"]["helper_class"]["init_args"]
                for env_var, env_value in env_map.items():
                    if env_value is None:
                        logging.error(
                            "env_var ${} is NULL and it's required for client config".format(
                                env_var
                            )
                        )
                        continue
                    clientconfig_str = clientconfig_str.replace(
                        "${}".format(env_var), env_value
                    )
                    dbinit_str = dbinit_str.replace("${}".format(env_var), env_value)
                    logging.info(
                        "replaced env_var ${} with the proper value on clientconfig".format(
                            env_var
                        )
                    )
                specs[filename]["clientconfig"] = json.loads(clientconfig_str)

                class_name = final_spec["db"]["helper_class"]["name"]
                logging.info("Creating DB helper from class {}".format(class_name))
                if class_name == "RedisVanilla":
                    specs[filename]["db_wrapper"] = RedisVanilla(json.loads(dbinit_str))
            else:
                logging.error(
                    "Filename with config {} is not a valid benchmark spec. Skipping it".format(
                        filename
                    )
                )
    logging.info(
        "Final benchmark specs  the following benchmark configs: \n\t{}".format(
            "\n\t".join([str(x) for x in specs.keys()])
        )
    )
    return result, specs
