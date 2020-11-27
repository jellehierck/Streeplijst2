import yaml
from pathlib import Path
from datetime import datetime

CONFIG_FOLDER = Path(__file__).resolve().parent
INSTANCE_FOLDER = Path(__file__).resolve().parent.parent.parent / 'instance'

########################
# Global configuration #
########################

config_path = CONFIG_FOLDER / 'config.yaml'
with open(config_path) as file:
    global_cfg = yaml.safe_load(file)

PORT = global_cfg['PORT']
UPDATE_INTERVAL = global_cfg['UPDATE_INTERVAL']
TIMEOUT = global_cfg['TIMEOUT']
BASE_URL = global_cfg['BASE_URL']
BASE_HEADER = global_cfg['BASE_HEADER']

###########################
# Sensitive configuration #
###########################

# NOTE: These configurations are located in the .yaml file below. !! Never share the contents of this file !!
credential_file_path = INSTANCE_FOLDER / 'credentials.yaml'  # Load the credential file
with open(credential_file_path) as file:
    secret_credentials = yaml.safe_load(file)

DEV_KEY = secret_credentials['DEV_KEY']  # Development key (not sensitive)
SECRET_KEY = secret_credentials['SECRET_KEY']  # Secret key for Flask app (sensitive if this app is accessed remotely)
TOKEN = secret_credentials['TOKEN']  # Token used to make API calls to Congressus
BASE_HEADER['Authorization'] += TOKEN

#######################
# Admin configuration #
#######################

admin_file_path = CONFIG_FOLDER / 'admin_config.yaml'  # Load the admin default configuration
with open(admin_file_path) as file:
    admin_cfg = yaml.safe_load(file)

DEFAULT_ADMIN = admin_cfg['DEFAULT_ADMIN']

#############################
# Streeplijst configuration #
#############################

streeplijst_config_path = CONFIG_FOLDER / 'streeplijst_config.yaml'
with open(streeplijst_config_path) as file:
    streeplijst_cfg = yaml.safe_load(file)

FOLDERS_META = streeplijst_cfg['FOLDERS_META']

##################################
# Streeplijst test configuration #
##################################

streeplijst_test_config_path = CONFIG_FOLDER / 'streeplijst_test_config.yaml'
with open(streeplijst_test_config_path) as file:
    streeplijst_test_cfg = yaml.safe_load(file)

TEST_USER = streeplijst_test_cfg['TEST_USER']
TEST_USER['date_of_birth'] = datetime.strptime(TEST_USER['date_of_birth'], '%d-%m-%Y')

TEST_USER_NO_SDD = streeplijst_test_cfg['TEST_USER_NO_SDD']
TEST_USER_NO_SDD['date_of_birth'] = datetime.strptime(TEST_USER_NO_SDD['date_of_birth'], '%d-%m-%Y')

TEST_ITEM = streeplijst_test_cfg['TEST_ITEM']
TEST_ITEM_2 = streeplijst_test_cfg['TEST_ITEM_2']
TEST_FOLDER_ID = streeplijst_test_cfg['TEST_FOLDER_ID']
TEST_FOLDER = FOLDERS_META[TEST_FOLDER_ID]
