#  Apache License Version 2.0
#
#  Copyright (c) 2021., Redis Performance Group
#  All rights reserved.
#

import os
import logging
import re

from .common import priority_merge_dict


def extract_inventory_spec(benchmark_config, inventory_keyname="inventory"):
    spec = None
    result = False
    if benchmark_config is not None:
        for k, v in benchmark_config.items():
            if inventory_keyname == k:
                spec = v
                result = True
    return result, spec


def merge_default_inventory_spec(
    benchmark_config, default_config, inventory_keyname="inventory"
):
    final_spec = None
    final_result = False
    benchmark_result, benchmark_spec = extract_inventory_spec(
        benchmark_config, inventory_keyname
    )
    default_result, default_spec = extract_inventory_spec(
        default_config, inventory_keyname
    )
    if benchmark_result is True or default_result is True:
        final_result = True
        # default was the only not empty
        if benchmark_result is False:
            final_spec = default_spec
        # benchmark was the only not empty
        elif default_result is False:
            final_spec = benchmark_spec
        # both are not empty. priorityse benchmark specific spec keys
        else:
            # declaring priority order
            final_spec = priority_merge_dict(benchmark_spec, default_spec)
    else:
        logging.warning(
            "While trying to merge the benchmark and default specs, both of them were empty on inventory key."
        )
    return final_result, final_spec


def get_db_env_map(inventory_spec, db_keyname="db"):
    env_map = {}
    result = True
    if db_keyname in inventory_spec:
        if "env" in inventory_spec[db_keyname]:
            for env_var_name in inventory_spec[db_keyname]["env"]:
                env_var_value = os.getenv(env_var_name, None)
                if env_var_value is None:
                    result &= False
                    logging.error(
                        "The required env var {} is not present. Failing DB env map setup.".format(
                            env_var_name
                        )
                    )
                env_map[env_var_name] = env_var_value
    return result, env_map


def extract_benchmark_tool_settings(benchmark_config):
    benchmark_tool = None
    benchmark_tool_source = None
    benchmark_tool_source_inner_path = None
    benchmark_min_tool_version = None
    benchmark_min_tool_version_major = None
    benchmark_min_tool_version_minor = None
    benchmark_min_tool_version_patch = None
    if "tool" in benchmark_config:
        benchmark_tool = benchmark_config["tool"]
    if "tool_source" in benchmark_config:
        if "remote" in benchmark_config["tool_source"]:
            benchmark_tool_source = benchmark_config["tool_source"]["remote"]
        if "bin_path" in benchmark_config["tool_source"]:
            benchmark_tool_source_inner_path = benchmark_config["tool_source"][
                "bin_path"
            ]

    if "min-tool-version" in benchmark_config:
        benchmark_min_tool_version = benchmark_config["min-tool-version"]
        p = re.compile(r"(\d+)\.(\d+)\.(\d+)")
        m = p.match(benchmark_min_tool_version)
        if m is None:
            logging.error(
                "Unable to extract semversion from 'min-tool-version'."
                " Will not enforce version"
            )
            benchmark_min_tool_version = None
        else:
            benchmark_min_tool_version_major = m.group(1)
            benchmark_min_tool_version_minor = m.group(2)
            benchmark_min_tool_version_patch = m.group(3)
    return (
        benchmark_min_tool_version,
        benchmark_min_tool_version_major,
        benchmark_min_tool_version_minor,
        benchmark_min_tool_version_patch,
        benchmark_tool,
        benchmark_tool_source,
        benchmark_tool_source_inner_path,
    )
