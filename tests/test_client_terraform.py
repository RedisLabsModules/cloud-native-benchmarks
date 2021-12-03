import yaml

from cloud_native_benchmarks.inventory.client_terraform import (
    get_client_terraform_spec,
    setup_terraform_from_remote,
    spin_terraform_client,
)
from cloud_native_benchmarks.inventory.config import merge_default_inventory_spec


def test_get_client_terraform_spec():
    with open(
        "./benchmarks/document/ycsb-commerce-rediscloud-redisjson-25primaries-load-1Mdocs.yml",
        "r",
    ) as yml_file:
        benchmark_config = yaml.safe_load(yml_file)
    with open("./benchmarks/document/defaults.yml", "r") as yml_file:
        default_config = yaml.safe_load(yml_file)

    _, final_spec = merge_default_inventory_spec(benchmark_config, default_config)
    result, source, branch, path, private_key_map = get_client_terraform_spec(
        final_spec
    )
    assert result == True
    assert source == "https://github.com/RedisLabsModules/testing-infrastructure"
    assert branch == "master"
    assert path == "/terraform/oss-1node-c5.4xlarge"
    assert private_key_map["from_env"] == "CNB_KEY"

    terraform_working_dir = setup_terraform_from_remote(path, source, branch)
    assert terraform_working_dir.endswith(path)


#
# def test_spin_terraform_client():
#     with open(
#         "./benchmarks/document/ycsb-commerce-rediscloud-redisjson-load.yml", "r"
#     ) as yml_file:
#         benchmark_config = yaml.safe_load(yml_file)
#     with open("./benchmarks/document/defaults.yml", "r") as yml_file:
#         default_config = yaml.safe_load(yml_file)
#
#     _, final_spec = merge_default_inventory_spec(benchmark_config, default_config)
#     result, source, branch, path, private_key_map = get_client_terraform_spec(
#         final_spec
#     )
#     assert result == True
#     assert source == "https://github.com/RedisLabsModules/testing-infrastructure"
#     assert branch == "master"
#     assert path == "/terraform/oss-1node-c5.4xlarge"
#     assert private_key_map["from_env"] == "CNB_KEY"
#     terraform_bin = "terraform"
#     tf_setup_name = "test-1"
#
#     terraform_working_dir = setup_terraform_from_remote(path, source, branch)
#     spin_terraform_client(
#         terraform_working_dir,
#         private_key_map,
#         {},
#         tf_setup_name,
#         terraform_bin,
#     )
