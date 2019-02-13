class BaseError(Exception):
    pass


class SlackClientConnectionFailed(BaseError):
    pass
