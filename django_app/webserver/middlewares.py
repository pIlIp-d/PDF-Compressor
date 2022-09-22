import string
from django.utils.crypto import get_random_string


class UserIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # create new user_id if not exists in session or cookie
        if 'user_id' in request.session:
            user_id = request.session["user_id"]
        elif "user_id" in request.COOKIES:
            user_id = request.COOKIES["user_id"]
        else:
            user_id = self.new_user_id()
        # TODO expand to also allow User from django auth (-> multiple devices from a single user are possible)

        request.session['user_id'] = user_id
        response = self.get_response(request)
        response.set_cookie("user_id", user_id)
        return response

    @staticmethod
    def new_user_id() -> str:
        return get_random_string(50, allowed_chars=(string.ascii_letters + string.digits))
