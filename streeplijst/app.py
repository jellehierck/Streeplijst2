import streeplijst.items as items
import streeplijst.api as api


class User:
    def __init__(self, s_number):
        self.s_number = s_number

        user_details = api.get_user(s_number)  # GET all user details from the API and store relevant details
        self.user_id = user_details["id"]
        self.first_name = user_details["first_name"]
        self.last_name_prefix = user_details["primary_last_name_prefix"]
        self.last_name = user_details["primary_last_name_main"]
        self.date_of_birth = user_details["date_of_birth"]
        self.has_sdd_mandate = user_details["has_sdd_mandate"]

        if user_details["profile_picture"] is None:  # Store a profile picture URL if the user has one.
            self.profile_picture = ""
        else:
            self.profile_picture = user_details["profile_picture"]["url_md"]


if __name__ == "__main__":
    folder_speciaal = items.get_folder_from_config("Speciaal")
    # folders = items.get_all_folders_from_config()
    user = User("s9999999")

    item = folder_speciaal.items[13591]
    sale = items.Sale(user, item, 1)
    sale.submit_sale()
