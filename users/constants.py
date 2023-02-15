class RequestKeys:
    USERNAME = 'username'
    EMAIL = 'email'
    PASSWORD = 'password'
    ROLE = 'role'
    FIRST_NAME = 'firstName'


class ResponseKeys:
    SESSION_TOKEN = 'sessionToken'
    ID = 'id'
    MESSAGE = 'message'
    EMAIL = 'email'
    USERNAME = 'username'
    FIRST_NAME = 'firstName'
    USER_INFO = 'userInfo'
    SUCCESS = 'success'


class ErrorMessages:
    DUPLICATE_USER = "Bad Request: User already exists."
    MISSING_FIELDS = "Bad Request: Missing fields {}"
    LOGIN_ERROR = "Invalid login credentials"
