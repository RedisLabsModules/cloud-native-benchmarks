#  Apache License Version 2.0
#
#  Copyright (c) 2021., Redis
#  All rights reserved.
#

import yaml
import os

from cloud_native_benchmarks.inventory.config import (
    get_db_env_map,
    merge_default_inventory_spec,
    extract_inventory_spec,
)


def test_get_db_env_map():
    with open(
        "./benchmarks/document/ycsb-commerce-rediscloud-redisjson-25primaries-load-1Mdocs.yml",
        "r",
    ) as yml_file:
        benchmark_config = yaml.safe_load(yml_file)
        res_bench, benchmark_spec = extract_inventory_spec(benchmark_config)

        for env_name in [
            "RC_JSON_HOST",
            "RC_JSON_USER",
            "RC_JSON_PORT",
            "RC_JSON_PASS",
        ]:
            if env_name in os.environ:
                del os.environ[env_name]

        db_env_result, db_env_map = get_db_env_map(benchmark_spec)
        assert db_env_result == False
        assert len(db_env_map.keys()) == 4

        os.environ["RC_JSON_HOST"] = "1"
        os.environ["RC_JSON_USER"] = "2"
        os.environ["RC_JSON_PORT"] = "3"
        os.environ["RC_JSON_PASS"] = "4"

        db_env_result, db_env_map = get_db_env_map(benchmark_spec)
        assert db_env_result == True
        assert len(db_env_map.keys()) == 4
        assert db_env_map["RC_JSON_HOST"] == "1"
        assert db_env_map["RC_JSON_USER"] == "2"
        assert db_env_map["RC_JSON_PORT"] == "3"
        assert db_env_map["RC_JSON_PASS"] == "4"


def test_merge_default_inventory_spec():
    benchmark_config = {}
    default_config = {}
    with open(
        "./benchmarks/document/ycsb-commerce-rediscloud-redisjson-25primaries-load-1Mdocs.yml",
        "r",
    ) as yml_file:
        benchmark_config = yaml.safe_load(yml_file)
    with open("./benchmarks/document/defaults.yml", "r") as yml_file:
        default_config = yaml.safe_load(yml_file)

    res_bench, benchmark_spec = extract_inventory_spec(benchmark_config)
    res_default, default_spec = extract_inventory_spec(default_config)
    assert len(default_spec.keys()) == 1
    assert len(benchmark_spec.keys()) == 1

    db_env_result, final_spec = merge_default_inventory_spec(
        benchmark_config, default_config
    )
    assert db_env_result == True
    # db and client
    assert len(final_spec.keys()) == 2
    assert "client" in final_spec.keys()
    assert "db" in final_spec.keys()
    assert (
        "https://github.com/RedisLabsModules/testing-infrastructure"
        == final_spec["client"]["terraform"]["source"]
    )
    assert "aws" == final_spec["db"]["cloud_provider"]
