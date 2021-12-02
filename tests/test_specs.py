from cloud_native_benchmarks.runner.specs import get_benchmark_specs


def test_get_benchmark_specs():
    specs = get_benchmark_specs("./benchmarks/document", "defaults.yml")
    assert len(specs) == 1
