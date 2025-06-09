from django.middleware.csrf import CsrfViewMiddleware
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
    

class DynamicCsrfViewMiddleware(CsrfViewMiddleware):    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        host = request.headers.get('X-Forwarded-Host') or request.get_host()
        scheme = request.scheme
        trusted_origin = f"{scheme}://{host}{f':{settings.ALLOWED_PORT}' if settings.ALLOWED_PORT else '' }"

        if trusted_origin not in settings.CSRF_TRUSTED_ORIGINS:
            settings.CSRF_TRUSTED_ORIGINS.append(trusted_origin)

        return super().process_view(request, callback, callback_args, callback_kwargs)
