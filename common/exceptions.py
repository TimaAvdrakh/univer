from rest_framework.exceptions import APIException
from rest_framework import status


class CustomException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'invalid'
    default_key = 'message'

    def __init__(self, key=default_key, detail=default_detail, status_code=status_code):
        if status_code != self.status_code:
            self.status_code = status_code

        self.detail = {
            key: detail
        }
