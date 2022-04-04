#!/usr/bin/env python3
"""This script updates a callforwards profile (CFP) on Cloudya (by NFON) to
an other phonenumber and profile name without a web browser."""

import yaml
from cloudya import Cloudya

def load_config():
    """Returns configuration from file"""
    with open('config.yaml', 'r', encoding='UTF-8') as file:
        return yaml.safe_load(file)


# Load configuration
config=load_config()
cloudya_username = config['cloudya']['auth']['username']
cloudya_password = config['cloudya']['auth']['password']
cloudya_cfp_alias = config['cloudya']['cfp']['alias']
cloudya_cfp_number = config['cloudya']['cfp']['number']
cloudya_cfp_phonenumber = config['cloudya']['cfp']['phonenumber']

# Init Cloudya
cloudya = Cloudya(auth_user=cloudya_username,
    auth_pass=cloudya_password)

# Update callforwards profile
cloudya.setup_cfp(cfp_alias=cloudya_cfp_alias,
    cfp_number=cloudya_cfp_number,
    cfp_phonenumber=cloudya_cfp_phonenumber)
