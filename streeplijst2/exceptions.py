import requests


class Streeplijst2Exception(Exception):
    """Base error for any custom exceptions in this application."""


class NotInDatabaseException(Streeplijst2Exception):
    """Error when an object could not be loaded from the database and it is insufficient to return None."""


class TotalPriceMismatchWarning(UserWarning, Streeplijst2Exception):
    """Warning when the total price of the sale does not match between the locally stored value and the value returned
    by the API."""
    pass


class UserNotSignedException(requests.exceptions.HTTPError, Streeplijst2Exception):
    """Error when the user has no signed SDD mandate."""
    pass


class NotFoundException(requests.exceptions.HTTPError, Streeplijst2Exception):
    """Error when something is not found."""
    pass


class ItemNotFoundException(NotFoundException):
    """Error when the item is not found."""
    pass


class FolderNotFoundException(NotFoundException):
    """Error when the folder is not found."""
    pass


class UserNotFoundException(NotFoundException):
    """Error when the user is not found."""
    pass
