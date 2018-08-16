from rest_framework_json_api.serializers import *
from .utils import custom_get_resource_type_from_instance, is_response_format_v2


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
        super(ResourceIdentifierSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        if not ('request' in self.context and is_response_format_v2(self.context['request'])):
            represent_data = super(ResourceIdentifierSerializer, self).to_representation(instance)
            represent_data['object'] = custom_get_resource_type_from_instance(instance)
            return represent_data

        ret = OrderedDict()
        fields = self._readable_fields
        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            if attribute is None:
                ret[field.field_name] = None
            else:
                field_data = field.to_representation(attribute)
                if hasattr(self.Meta, 'nested_fields') and field.field_name in self.Meta.nested_fields:
                    field_data = {
                        "data": field_data,
                        "meta": {
                            "include": [],
                            "custom": []
                        }
                    }
                ret[field.field_name] = field_data
        represent_data = ret

        data = {
            'object': custom_get_resource_type_from_instance(instance)
        }
        for item in represent_data.items():
            data[item[0]] = item[1]

        return data