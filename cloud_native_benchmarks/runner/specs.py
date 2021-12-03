#  Apache License Version 2.0
#
#  Copyright (c) 2021., Redis Performance Group
#  All rights reserved.
#

import logging
import pathlib

import yaml

from cloud_native_benchmarks.inventory.config import merge_default_inventory_spec


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
    for filename in files:
        with open(filename, "r") as yml_file:
            benchmark_config = yaml.safe_load(yml_file)
            spec_result, final_spec = merge_default_inventory_spec(
                benchmark_config, default_config
            )

            if spec_result is True:
                specs[filename] = {}
                specs[filename]["test_name"] = benchmark_config["name"]
                specs[filename]["inventory"] = final_spec
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
    return specs
