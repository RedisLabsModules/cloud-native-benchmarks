import logging
import os


def check_and_fix_pem_str(ec2_private_pem: str):
    pem_str = ec2_private_pem.replace("-----BEGIN RSA PRIVATE KEY-----", "")
    pem_str = pem_str.replace("-----END RSA PRIVATE KEY-----", "")
    pem_str = pem_str.replace(" ", "\n")
    pem_str = "-----BEGIN RSA PRIVATE KEY-----\n" + pem_str
    pem_str = pem_str + "-----END RSA PRIVATE KEY-----\n"
    # remove any dangling whitespace
    pem_str = os.linesep.join([s for s in pem_str.splitlines() if s])
    return pem_str


def ssh_pem_check(EC2_PRIVATE_PEM, private_key):
    if EC2_PRIVATE_PEM is not None and EC2_PRIVATE_PEM != "":
        with open(private_key, "w") as tmp_private_key_file:
            pem_str = check_and_fix_pem_str(EC2_PRIVATE_PEM)
            tmp_private_key_file.write(pem_str)
    if os.path.exists(private_key) is False:
        logging.error(
            "Specified private key path does not exist: {}".format(private_key)
        )
        exit(1)
    else:
        logging.info(
            "Confirmed that private key path artifact: '{}' exists!".format(private_key)
        )
