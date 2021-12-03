import os

from cloud_native_benchmarks.runner.specs import get_benchmark_specs


def test_get_benchmark_specs():
    os.environ["RC_JSON_HOST"] = "localhost"
    os.environ["RC_JSON_USER"] = "default"
    os.environ["RC_JSON_PORT"] = "6379"
    os.environ["RC_JSON_PASS"] = ""
    os.environ["RC_JSON_CLUSTER_ENABLED"] = "false"
    res, final_specs = get_benchmark_specs("./tests/test_data", "defaults.yml")
    assert len(final_specs) == 1
    assert res == True
    final_spec = list(final_specs.values())[0]
    assert (
        final_spec["clientconfig"]["parameters"]["override_workload_properties"][
            "redis.host"
        ]
        == "localhost"
    )
    assert (
        final_spec["clientconfig"]["parameters"]["override_workload_properties"][
            "redis.port"
        ]
        == "6379"
    )
    assert (
        final_spec["clientconfig"]["parameters"]["override_workload_properties"][
            "redis.user"
        ]
        == "default"
    )
    assert (
        final_spec["clientconfig"]["parameters"]["override_workload_properties"][
            "redis.pass"
        ]
        == ""
    )
