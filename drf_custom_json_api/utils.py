from rest_framework_json_api.utils import *


def custom_get_resource_type_from_instance(instance):
    #check if have custom field for mongo model
    if isinstance(instance._meta, dict) and "object_name" in instance._meta:
        return str(instance._meta["object_name"])
    else:
        return get_resource_type_from_instance(instance)



def get_response_format_from_request(request):
	return request.query_params.get('response-format', '')


def is_response_format_v2(request):
	version = get_response_format_from_request(request)
	if str(version).lower() == 'v2':
		return True
	return False
