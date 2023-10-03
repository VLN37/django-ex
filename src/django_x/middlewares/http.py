# Standard Library
from io import BytesIO
import logging

# Third Party
from asgiref.sync import iscoroutinefunction
from django.conf import settings as django_settings
from django.http import QueryDict
from django.http.multipartparser import MultiPartParserError, TooManyFilesSent
from django.utils.decorators import sync_and_async_middleware

logger = logging.getLogger("django_x")

def _load_data_and_files(request):
    if request.content_type == "multipart/form-data":
        if hasattr(request, "_body"):
            # Use already read data
            data = BytesIO(request._body)
        else:
            data = request
        try:
            DATA, FILES = request.parse_file_upload(request.META, data)
            request.FILES.update(FILES)
        except (MultiPartParserError, TooManyFilesSent) as exc:
            request._mark_post_parse_error()
            raise exc
    elif request.content_type == "application/x-www-form-urlencoded":
        DATA = QueryDict(request.body, encoding=django_settings.DEFAULT_CHARSET)
    else:
        logger.info("Unsupported request content_type. You have to parse body by hand")
        DATA = QueryDict(encoding=django_settings.DEFAULT_CHARSET)
    return DATA

@sync_and_async_middleware
def ProtocolExtensionMiddleware(get_response):
    if iscoroutinefunction(get_response):
        async def protocol_extension_middleware(request):
            method_name = request.method.upper()
            if method_name in ["PUT", "PATCH", "DELETE"]:
                setattr(request, method_name, _load_data_and_files(request))
            if method_name in ["POST", "PUT", "PATCH", "DELETE"]:
                if hasattr(request, "data"):
                    new_data = request.data.copy().update(getattr(request, method_name))
                    request.data = new_data
                    request.data._mutable = False
                else:
                    request.data = getattr(request, method_name)
            response = await get_response(request)
            return response
    else:
        def protocol_extension_middleware(request):
            method_name = request.method.upper()
            if method_name in ["PUT", "PATCH", "DELETE"]:
                setattr(request, method_name, _load_data_and_files(request))
            if method_name in ["POST", "PUT", "PATCH", "DELETE"]:
                if hasattr(request, "data"):
                    new_data = request.data.copy().update(getattr(request, method_name))
                    request.data = new_data
                    request.data._mutable = False
                else:
                    request.data = getattr(request, method_name)
            response = get_response(request)
            return response

    return protocol_extension_middleware
