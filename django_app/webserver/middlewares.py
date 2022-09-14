import uuid


class UserIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # create new user_id if not exists in session or cookie
        user_id = self.new_user_id() if 'user_id' not in request.session and "user_id" not in request.COOKIES \
            else request.session["user_id"] or request.COOKIES["user_id"]
        # TODO expand to also allow User from django auth (-> multiple devices from a single user are possible)

        request.session['user_id'] = user_id
        response = self.get_response(request)
        response.set_cookie("user_id", user_id)
        return response

    @staticmethod
    def new_user_id() -> str:
        return str(uuid.uuid1())
