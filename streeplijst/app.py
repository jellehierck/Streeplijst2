import requests
import json

import streeplijst.items as items


if __name__ == "__main__":
    items.get_folder_from_config("Speciaal")

    folders = items.get_all_folders_from_config()