from rest_framework_json_api.serializers import *


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

    def to_representation(self, instance):
        represent_data = super(ResourceIdentifierSerializer, self).to_representation(instance)
        data = {
            'object': get_resource_type_from_instance(instance)
        }
        for item in represent_data.items():
            data[item[0]] = item[1]
        return data