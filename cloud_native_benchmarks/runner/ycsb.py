def prepare_ycsb_benchmark_command(
    executable_path: str,
    benchmark_config: object,
    current_workdir,
):
    """
    Prepares ycsb command parameters
    :param executable_path:
    :param benchmark_config:
    :param current_workdir:
    :return: [string] containing the required command to run the benchmark given the configurations
    """
    command_arr = [executable_path]

    # we need the csv output
    database = None
    step = None
    workload = None
    override_workload_properties = []
    k = benchmark_config["parameters"]
    if "database" in k:
        database = k["database"]
    if "step" in k:
        step = k["step"]
    if "workload" in k:
        workload = k["workload"]
        if current_workdir is not None and workload.startswith("./"):
            workload = "{}{}".format(current_workdir, workload[1:])
    if "override_workload_properties" in k:
        override_workload_properties = k["override_workload_properties"]

    command_arr.append(step)
    command_arr.append(database)

    command_arr.extend(["-P", "{}".format(workload)])

    for k, v in override_workload_properties.items():
        if current_workdir is not None and type(v) == str and v.startswith("./"):
            v = "{}{}".format(current_workdir, v[1:])
        command_arr.extend(["-p", "{}={}".format(k, v)])

    command_str = " ".join(command_arr)
    return command_arr, command_str
