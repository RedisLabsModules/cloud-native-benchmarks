#  Apache License Version 2.0
#
#  Copyright (c) 2021., Redis Performance Group
#  All rights reserved.
#


def priority_merge_dict(priority_one, priority_two):
    prio_dict = {1: priority_one, 2: priority_two}
    final_spec = prio_dict[2].copy()
    for key, val in prio_dict[1].items():
        final_spec[key] = val
    return final_spec


def get_run_full_filename(
    start_time_str,
    test_name,
):
    benchmark_output_filename = "{start_time_str}-{test_name}.json".format(
        start_time_str=start_time_str, test_name=test_name
    )
    return benchmark_output_filename
