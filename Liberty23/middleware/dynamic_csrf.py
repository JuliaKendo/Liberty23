from django.conf import settings

class DynamicCsrfTrustedOriginsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = f"{request.scheme}://{request.get_host()}"

        forwarded_host = request.headers.get('X-Forwarded-Host')
        if forwarded_host:
            host = f"{request.scheme}://{forwarded_host}{f':{settings.ALLOWED_PORT}' if settings.ALLOWED_PORT else '' }"

        if host not in settings.CSRF_TRUSTED_ORIGINS:
            settings.CSRF_TRUSTED_ORIGINS.append(host)
        response = self.get_response(request)

        return response
