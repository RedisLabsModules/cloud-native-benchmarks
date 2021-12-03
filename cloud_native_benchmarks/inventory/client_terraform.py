#  Apache License Version 2.0
#
#  Copyright (c) 2021., Redis Performance Group
#  All rights reserved.
#


import logging
import tempfile

import git
from python_terraform import Terraform, IsNotFlagged

from cloud_native_benchmarks.inventory.common import priority_merge_dict


def setup_terraform_from_remote(
    folder,
    repo="https://github.com/RedisLabsModules/testing-infrastructure.git",
    branch="master",
):
    # fetch terraform folder
    temporary_dir = tempfile.mkdtemp()
    logging.info(
        "Fetching infrastructure definition from git repo {}/{} (branch={})".format(
            repo, folder, branch
        )
    )
    git.Repo.clone_from(repo, temporary_dir, branch=branch, depth=1)
    terraform_working_dir = temporary_dir + folder
    return terraform_working_dir


def get_client_terraform_spec(
    inventory_spec, client_key="client", terraform_key="terraform"
):
    result = False
    path_result = False
    private_key_result = False
    private_key_map = {
        "variable": "private_key",
        "location": "/tmp/benchmarks.redislabs.pem",
        "from_env": None,
    }
    source = "https://github.com/RedisLabsModules/testing-infrastructure"
    branch = "master"
    path = None
    if client_key in inventory_spec:
        if terraform_key in inventory_spec[client_key]:
            terraform_spec = inventory_spec[client_key][terraform_key]
            # path and private_key.from_env are the minimum requirements
            if "path" in terraform_spec:
                path = terraform_spec["path"]
                path_result = True
            if "source" in terraform_spec:
                source = terraform_spec["source"]
            if "branch" in terraform_spec:
                branch = terraform_spec["branch"]
            if "private_key" in terraform_spec:
                private_key = terraform_spec["private_key"]
                private_key_map = priority_merge_dict(private_key, private_key_map)
                if private_key_map["from_env"] is not None:
                    private_key_result = True
    result = path_result & private_key_result

    return result, source, branch, path, private_key_map


def tf_output_or_none(tf_output, output_prop):
    res = None
    if output_prop in tf_output:
        res = tf_output[output_prop]["value"][0]
    return res


def retrieve_tf_connection_vars(tf):
    tf_output = tf.output()
    client_public_ip = tf_output_or_none(tf_output, "client_public_ip")
    client_private_ip = tf_output_or_none(tf_output, "client_private_ip")
    return (
        client_private_ip,
        client_public_ip,
    )


def spin_terraform_client(
    terraform_working_dir,
    private_key_map,
    variable_map,
    tf_setup_name,
    terraform_bin,
):
    tf_variable = private_key_map["variable"]
    tf_variable_value = private_key_map["location"]
    tf_variable_dict = priority_merge_dict(
        {tf_variable: tf_variable_value, "setup_name": tf_setup_name}, variable_map
    )
    tf = Terraform(
        working_dir=terraform_working_dir,
        terraform_bin_path=terraform_bin,
        variables=tf_variable_dict,
    )
    tf_keyname = "cloud-native-benchmarks/infrastructure/{}.tfstate".format(
        tf_setup_name
    )
    logging.info(
        "Initing a terraform setup with backend key config named {}".format(tf_keyname)
    )
    _, _, _ = tf.init(
        capture_output=True,
        backend_config={"key": tf_keyname},
    )
    _, _, _ = tf.refresh()
    client_private_ip, client_public_ip = retrieve_tf_connection_vars(tf)
    if client_private_ip is not None or client_public_ip is not None:
        logging.warning("Destroying previous setup")
        tf.destroy()
    return_code, stdout, stderr = tf.apply(
        skip_plan=True,
        capture_output=False,
        refresh=True,
        var=tf_variable_dict,
    )
    client_private_ip, client_public_ip = retrieve_tf_connection_vars(tf)
    username = "ubuntu"
    return (return_code, username, client_private_ip, client_public_ip, tf)


def terraform_destroy(remote_envs):
    for remote_setup_name, tf_dict in remote_envs.items():
        # tear-down
        tf = tf_dict["tf"]
        logging.info("Tearing down setup {}".format(remote_setup_name))
        tf.destroy(
            capture_output="yes",
            no_color=IsNotFlagged,
            force=IsNotFlagged,
            auto_approve=True,
        )
        logging.info("Tear-down completed")
