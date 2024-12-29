from flask import Response, make_response

def make_error_response(error_message: str, status_code: int) -> Response:
    return make_response({"error": error_message}, status_code)

def make_success_response(success_message: str, status_code: int = 200) -> Response:
    return make_response({"message": success_message}, status_code)