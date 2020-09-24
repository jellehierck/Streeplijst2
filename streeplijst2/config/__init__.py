import yaml
from pathlib import Path

###########################
# Sensitive configuration #
###########################

# TODO: Check if this can also be done using .env files
credential_file_path = Path(__file__).resolve().parent.parent.parent / 'instance/credentials.yaml'  # Load the credential file
with open(credential_file_path) as file:
    creds = yaml.safe_load(file)

TOKEN = creds['TOKEN']
DEV_KEY = creds['DEV_KEY']
SECRET_KEY = creds['SECRET_KEY']

########################
# Global configuration #
########################
config_path = Path(__file__).resolve().parent / 'config.yaml'
with open(config_path) as file:
    cfg = yaml.safe_load(file)

TIMEOUT = cfg['TIMEOUT']
BASE_URL = cfg['BASE_URL']
BASE_HEADER = cfg['BASE_HEADER']
BASE_HEADER['Authorization'] += TOKEN

#############################
# Streeplijst configuration #
#############################

streeplijst_config_path = Path(__file__).resolve().parent / 'streeplijst_config.yaml'
with open(streeplijst_config_path) as file:
    sl_cfg = yaml.safe_load(file)

FOLDERS = sl_cfg['FOLDERS']

##################################
# Streeplijst test configuration #
##################################

streeplijst_test_config_path =config_path = Path(__file__).resolve().parent / 'streeplijst_test_config.yaml'
with open(streeplijst_test_config_path) as file:
    cfg = yaml.safe_load(file)

TEST_USER = cfg['TEST_USER']
TEST_USER_NO_SDD = cfg['TEST_USER_NO_SDD']
TEST_ITEM = cfg['TEST_ITEM']
TEST_FOLDER_ID = cfg['TEST_FOLDER_ID']
