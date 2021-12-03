#  Apache License Version 2.0
#
#  Copyright (c) 2021., Redis Performance Group
#  All rights reserved.
#
import os

import pkg_resources

SPECS_PATH_TEST_SUITES_DEFAULT_PATH = "./benchmarks/document"
try:
    SPECS_PATH_TEST_SUITES_DEFAULT_PATH = pkg_resources.resource_filename(
        "redis_benchmarks_specification", "benchmarks/document"
    )
except ModuleNotFoundError:
    pass

SPECS_PATH_TEST_SUITES = os.getenv(
    "SPECS_PATH_TEST_SUITES", SPECS_PATH_TEST_SUITES_DEFAULT_PATH
)
TERRAFORM_BIN_PATH = os.getenv("TERRAFORM_BIN_PATH", "terraform")
CNB_DATASINK_RTS_PUSH = bool(os.getenv("CNB_DATASINK_PUSH_RTS", False))
CNB_DATASINK_RTS_AUTH = os.getenv("CNB_DATASINK_RTS_AUTH", None)
CNB_DATASINK_RTS_USER = os.getenv("CNB_DATASINK_RTS_USER", None)
CNB_DATASINK_RTS_HOST = os.getenv("CNB_DATASINK_RTS_HOST", "localhost")
CNB_DATASINK_RTS_PORT = int(os.getenv("CNB_DATASINK_RTS_PORT", "6379"))
REDIS_HEALTH_CHECK_INTERVAL = int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "15"))
REDIS_SOCKET_TIMEOUT = int(os.getenv("REDIS_SOCKET_TIMEOUT", "300"))


def cli_args(parser):
    # common arguments to all tools
    parser.add_argument(
        "--version", default=False, action="store_true", help="print version and exit"
    )
    parser.add_argument(
        "--local-dir", type=str, default="./", help="local dir to use as storage"
    )
    parser.add_argument(
        "--defaults_filename",
        type=str,
        default="defaults.yml",
        help="specify the defaults file containing spec topologies, common metric extractions,etc...",
    )
    parser.add_argument(
        "--logname", type=str, default=None, help="logname to write the logs to"
    )
    parser.add_argument("--terraform_bin_path", type=str, default=TERRAFORM_BIN_PATH)
    parser.add_argument("--setup_name_sufix", type=str, default="")

    parser.add_argument(
        "--test-suites-folder",
        type=str,
        default=SPECS_PATH_TEST_SUITES,
        help="Test suites folder, containing the different test variations",
    )
    parser.add_argument(
        "--datasink_redistimeseries_host", type=str, default=CNB_DATASINK_RTS_HOST
    )
    parser.add_argument(
        "--datasink_redistimeseries_port", type=int, default=CNB_DATASINK_RTS_PORT
    )
    parser.add_argument(
        "--datasink_redistimeseries_pass", type=str, default=CNB_DATASINK_RTS_AUTH
    )
    parser.add_argument(
        "--datasink_redistimeseries_user", type=str, default=CNB_DATASINK_RTS_USER
    )
    parser.add_argument(
        "--datasink_push_results_redistimeseries",
        default=CNB_DATASINK_RTS_PUSH,
        action="store_true",
        help="uploads the results to RedisTimeSeries. Proper credentials are required",
    )
