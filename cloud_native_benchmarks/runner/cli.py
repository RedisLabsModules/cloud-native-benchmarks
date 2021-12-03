#  Apache License Version 2.0
#
#  Copyright (c) 2021., Redis Performance Group
#  All rights reserved.
#

import argparse

# import datetime
import logging
import os
import sys
import traceback

import redis
from redisbench_admin.run.common import (
    get_start_time_vars,
)
from redisbench_admin.run_remote.remote_client import (
    run_remote_benchmark,
)
from redisbench_admin.run_remote.remote_helpers import remote_tool_pre_bench_step

from cloud_native_benchmarks.inventory.client_terraform import (
    get_client_terraform_spec,
    setup_terraform_from_remote,
    spin_terraform_client,
    terraform_destroy,
)
from redistimeseries.client import Client

from .args import (
    cli_args,
    REDIS_HEALTH_CHECK_INTERVAL,
    REDIS_SOCKET_TIMEOUT,
)
from .log import log_setup
from .poetry import (
    populate_with_poetry_data,
    print_version,
)
from .specs import get_benchmark_specs
from .ssh import ssh_pem_check
from .ycsb import prepare_ycsb_benchmark_command
from ..inventory.common import get_run_full_filename
from ..inventory.config import extract_benchmark_tool_settings


def cli_logic(args):
    testsuites_folder = os.path.abspath(args.test_suites_folder)
    logging.info("Using test-suites folder dir {}".format(testsuites_folder))
    specs_setup_result, testsuite_specs = get_benchmark_specs(
        testsuites_folder, args.defaults_filename
    )
    if specs_setup_result is False:
        logging.warning("Error preparing SPEC. Exiting...")
        exit(1)
    logging.info(
        "There are a total of {} test-suites in folder {}".format(
            len(testsuite_specs), testsuites_folder
        )
    )
    if len(testsuite_specs) == 0:
        logging.warning("No benchmark SPEC found. Goodbye...")
        exit(0)

    remote_envs = {}
    rts = None
    return_code = 0
    if args.datasink_push_results_redistimeseries:
        logging.info(
            "Checking redistimeseries datasink connection is available at: {}:{} to push the timeseries data".format(
                args.datasink_redistimeseries_host, args.datasink_redistimeseries_port
            )
        )
        try:
            rts = Client(
                host=args.datasink_redistimeseries_host,
                port=args.datasink_redistimeseries_port,
                decode_responses=True,
                password=args.datasink_redistimeseries_pass,
                username=args.datasink_redistimeseries_user,
                health_check_interval=REDIS_HEALTH_CHECK_INTERVAL,
                socket_connect_timeout=REDIS_SOCKET_TIMEOUT,
                socket_keepalive=True,
            )
            rts.redis.ping()
        except redis.exceptions.ConnectionError as e:
            logging.error(
                "Unable to connect to redis available at: {}:{}".format(
                    args.datasink_redistimeseries_host,
                    args.datasink_redistimeseries_port,
                )
            )
            logging.error("Error message {}".format(e.__str__()))
            exit(1)

    logging.info("checking build spec requirements")
    for filename, spec in testsuite_specs.items():
        logging.info("Calling DBWrapper SETUP")
        spec["db_wrapper"].setup()

        test_name = spec["test_name"]
        result, source, branch, path, private_key_map = get_client_terraform_spec(
            spec["inventory"]
        )
        if result is False:
            logging.warning(
                "Unable to retrieve terraform client SPEC for {}. Passing...".format(
                    filename
                )
            )
            logging.info(private_key_map)
            continue

        terraform_inv_key = "{}{}{}".format(source, branch, path)
        EC2_PRIVATE_PEM = os.getenv(private_key_map["from_env"], None)
        ssh_pem_check(EC2_PRIVATE_PEM, private_key_map["location"])

        # after we've created the env, even on error we should always teardown
        # in case of some unexpected error we fail the test
        try:
            terraform_working_dir = setup_terraform_from_remote(path, source, branch)
            tf_setup_name = terraform_working_dir
            (
                tf_return_code,
                username,
                client_private_ip,
                client_public_ip,
                tf,
            ) = spin_terraform_client(
                terraform_working_dir,
                private_key_map,
                {},
                tf_setup_name,
                args.terraform_bin_path,
            )
            remote_envs[terraform_inv_key] = {
                "tf": tf,
                "client_public_ip": client_public_ip,
                "username": username,
                "client_private_ip": client_private_ip,
            }

            logging.info(
                "Using client machine with username={} client_public_ip={} client_private_ip={}".format(
                    username, client_public_ip, client_private_ip
                )
            )

            (
                start_time,
                start_time_ms,
                start_time_str,
            ) = get_start_time_vars()

            local_bench_fname = get_run_full_filename(
                start_time_str,
                test_name,
            )

            logging.info(
                "Will store benchmark result in file {}".format(local_bench_fname)
            )
            benchmark_config = spec["benchmark_config"]
            clientconfig = spec["clientconfig"]
            private_key = private_key_map["location"]

            (
                benchmark_min_tool_version,
                benchmark_min_tool_version_major,
                benchmark_min_tool_version_minor,
                benchmark_min_tool_version_patch,
                benchmark_tool,
                benchmark_tool_source,
                _,
            ) = extract_benchmark_tool_settings(clientconfig)
            client_ssh_port = 22
            # setup the benchmark tool
            remote_tool_pre_bench_step(
                benchmark_config,
                benchmark_min_tool_version,
                benchmark_min_tool_version_major,
                benchmark_min_tool_version_minor,
                benchmark_min_tool_version_patch,
                benchmark_tool,
                client_public_ip,
                username,
                benchmark_tool_source,
                "clientconfig",
                "ubuntu",
                "",
                client_ssh_port,
                private_key,
            )
            remote_results_file = "/tmp/results"
            if "ycsb" in benchmark_tool:
                benchmark_tool = "/tmp/ycsb/bin/ycsb"
                current_workdir = "/tmp/ycsb"
                command_arr, command_str = prepare_ycsb_benchmark_command(
                    benchmark_tool,
                    clientconfig,
                    current_workdir,
                )
            printed_command_str = command_str
            printed_command_arr = command_arr
            if len(command_str) > 500:
                printed_command_str = command_str[:500] + "... (trimmed output) ..."
                printed_command_arr = printed_command_arr[:1] + [
                    "(...) trimmed output...."
                ]
            logging.info(
                "Running the benchmark with the following parameters:\n\tArgs array: {}\n\tArgs str: {}".format(
                    printed_command_arr, printed_command_str
                )
            )

            # benchmark_start_time = datetime.datetime.now()
            # run the benchmark
            remote_run_result, stdout, _ = run_remote_benchmark(
                client_public_ip,
                username,
                private_key,
                remote_results_file,
                local_bench_fname,
                command_str,
                client_ssh_port,
            )
            # benchmark_end_time = datetime.datetime.now()

        except KeyboardInterrupt:
            logging.critical(
                "Detected Keyboard interrupt...Destroy all remote envs and exiting right away!"
            )
            terraform_destroy(remote_envs)
            exit(1)
        except:
            return_code |= 1
            logging.critical(
                "Some unexpected exception was caught "
                "during remote work. Failing test...."
            )
            logging.critical(sys.exc_info()[0])
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)

    terraform_destroy(remote_envs)
    exit(return_code)


def main():
    project_name, project_description, project_version = populate_with_poetry_data()
    parser = argparse.ArgumentParser(
        description=project_description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cli_args(parser)

    args = parser.parse_args()
    if args.version:
        print_version(project_name, project_version)
        exit(0)

    print_version(project_name, project_version)
    log_setup(args.logname)

    cli_logic(args)
