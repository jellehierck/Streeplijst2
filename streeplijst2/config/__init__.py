import yaml
from pathlib import Path
from datetime import datetime

###########################
# Sensitive configuration #
###########################

# TODO: Check if this can also be done using .env files
credential_file_path = Path(
    __file__).resolve().parent.parent.parent / 'instance/credentials.yaml'  # Load the credential file
with open(credential_file_path) as file:
    secret_credentials = yaml.safe_load(file)

TOKEN = secret_credentials['TOKEN']
DEV_KEY = secret_credentials['DEV_KEY']
SECRET_KEY = secret_credentials['SECRET_KEY']

########################
# Global configuration #
########################
config_path = Path(__file__).resolve().parent / 'config.yaml'
with open(config_path) as file:
    global_cfg = yaml.safe_load(file)

UPDATE_INTERVAL = global_cfg['UPDATE_INTERVAL']
TIMEOUT = global_cfg['TIMEOUT']
BASE_URL = global_cfg['BASE_URL']
BASE_HEADER = global_cfg['BASE_HEADER']
BASE_HEADER['Authorization'] += TOKEN

#############################
# Streeplijst configuration #
#############################

streeplijst_config_path = Path(__file__).resolve().parent / 'streeplijst_config.yaml'
with open(streeplijst_config_path) as file:
    streeplijst_cfg = yaml.safe_load(file)

FOLDERS = streeplijst_cfg['FOLDERS']

##################################
# Streeplijst test configuration #
##################################

streeplijst_test_config_path = config_path = Path(__file__).resolve().parent / 'streeplijst_test_config.yaml'
with open(streeplijst_test_config_path) as file:
    streeplijst_test_cfg = yaml.safe_load(file)

TEST_USER = streeplijst_test_cfg['TEST_USER']
TEST_USER['date_of_birth'] = datetime.strptime(TEST_USER['date_of_birth'], '%d-%m-%Y')

TEST_USER_NO_SDD = streeplijst_test_cfg['TEST_USER_NO_SDD']
TEST_USER_NO_SDD['date_of_birth'] = datetime.strptime(TEST_USER_NO_SDD['date_of_birth'], '%d-%m-%Y')

TEST_ITEM = streeplijst_test_cfg['TEST_ITEM']
TEST_ITEM_2 = streeplijst_test_cfg['TEST_ITEM_2']
TEST_FOLDER_ID = streeplijst_test_cfg['TEST_FOLDER_ID']
TEST_FOLDER = FOLDERS[TEST_FOLDER_ID]
