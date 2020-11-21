from requests import HTTPError, Timeout  # Needed for HTTP request errors


###################
# Base exceptions #
###################

class Streeplijst2Exception(Exception):
    """Base error for any custom exceptions in this application."""


class Streeplijst2Warning(UserWarning, Streeplijst2Exception):
    """Base warning for any custom warnings in this application."""


#######################
# Database exceptions #
#######################

class NotInDatabaseException(Streeplijst2Exception):
    """Error when an object could not be loaded from the database and it is insufficient to return None."""


class TotalPriceMismatchWarning(Streeplijst2Warning):
    """Warning when the total price of the sale does not match between the locally stored value and the value returned
    by the API."""
    pass


##################
# API exceptions #
##################

class UserNotSignedException(HTTPError, Streeplijst2Exception):
    """Error when the user has no signed SDD mandate."""
    pass


class NotFoundException(HTTPError, Streeplijst2Exception):
    """Error when something is not found during an HTTP request."""
    pass


class ItemNotFoundException(NotFoundException):
    """Error when the item is not found during an HTTP request."""
    pass


class FolderNotFoundException(NotFoundException):
    """Error when the folder is not found during an HTTP request."""
    pass


class UserNotFoundException(NotFoundException):
    """Error when the user is not found during an HTTP request."""
    pass
