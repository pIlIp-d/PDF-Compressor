import uuid


class UserIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # create new user_id if not exists
        if 'user_id' not in request.session:
            request.session['user_id'] = self.new_user_id()
            # TODO expand to also allow User from django auth (-> multiple devices from a single user are possible)
            # TODO cookie, because session isn't saved after reboot etc

        return self.get_response(request)

    @staticmethod
    def new_user_id() -> str:
        return str(uuid.uuid1())
