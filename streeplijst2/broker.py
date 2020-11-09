from streeplijst2.database import UserController, User
import streeplijst2.api as api


class APIDatabaseBroker:

    @classmethod
    def get_user(self, s_number: str, timeout: float = api.TIMEOUT) -> User:
        user_dict = api.get_user(s_number=s_number, timeout=timeout)
        user = UserController.create(**user_dict)
        return user


