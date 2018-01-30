from rest_framework_json_api.utils import *
from django.conf import settings


RESPONSE_VERSION_1 = 'v1'
RESPONSE_VERSION_2 = 'v2'

AVAILABLE_VERSIONS = [RESPONSE_VERSION_1, RESPONSE_VERSION_2]

def custom_get_resource_type_from_instance(instance):
    #check if have custom field for mongo model
    if hasattr(instance, '_meta') and isinstance(instance._meta, dict) and "object_name" in instance._meta:
        return str(instance._meta["object_name"])
    else:
        return get_resource_type_from_instance(instance)


def get_default_version():
    version = RESPONSE_VERSION_1
    if hasattr(settings, "RESPONSE_FORMAT_VERSION"):
        version = settings.RESPONSE_FORMAT_VERSION if settings.RESPONSE_FORMAT_VERSION in AVAILABLE_VERSIONS else RESPONSE_VERSION_1
    return version

def get_response_format_from_request(request):
    version = str(request.query_params.get('response-format', '')).lower()
    if version not in AVAILABLE_VERSIONS:
        version = get_default_version()
    return version


def is_response_format_v2(request):
    version = get_response_format_from_request(request)
    if version == RESPONSE_VERSION_2:
        return True
    return False
