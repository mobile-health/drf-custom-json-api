from rest_framework_json_api.serializers import *
from .utils import custom_get_resource_type_from_instance, is_response_format_v1


class NotUpdateSerializerMixin(object):

    def __init__(self, *args, **kwargs):
        super(NotUpdateSerializerMixin, self).__init__(*args, **kwargs)
        if kwargs.get("context", None):
            request = kwargs['context']['request']
            if request.method in ["PUT", "PATCH"]:
                if hasattr(self.Meta, "no_update_fields"):
                    current_read_only_fields = getattr(self.Meta, "read_only_fields", [])
                    self.Meta.read_only_fields = set(list(current_read_only_fields) + list(self.Meta.no_update_fields))


class ResourceIdentifierSerializer(object):
    def __init__(self, *args, **kwargs):
        self.Meta.is_nested = kwargs.pop("is_nested", False)
        super(ResourceIdentifierSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        represent_data = super(ResourceIdentifierSerializer, self).to_representation(instance)
        
        # Support only response formart v1
        return represent_data
        
        # if is_response_format_v1(self.context['request']):
        #     return represent_data

        # data = {
        #     'object': custom_get_resource_type_from_instance(instance)
        # }
        # for item in represent_data.items():
        #     data[item[0]] = item[1]
        # if self.Meta.is_nested:
        #     data = {
        #         "data": data,
        #         "meta": {
        #             "include": [],
        #             "custom": []
        #         }
        #     }
        # return data