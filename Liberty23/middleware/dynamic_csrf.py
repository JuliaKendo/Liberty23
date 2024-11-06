from django.conf import settings

class DynamicCsrfTrustedOriginsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = f"{request.scheme}://{request.get_host()}"
        if host not in settings.CSRF_TRUSTED_ORIGINS:
            settings.CSRF_TRUSTED_ORIGINS.append(host)
        response = self.get_response(request)
        return response
