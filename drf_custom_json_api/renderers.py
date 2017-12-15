from __future__ import unicode_literals

from collections import OrderedDict
from rest_framework_json_api import renderers
from django.utils import encoding, six
from rest_framework.settings import api_settings
from . import utils


class JSONRenderer(renderers.JSONRenderer):

    @classmethod
    def extract_attributes(cls, fields, resource):
        data = OrderedDict()
        for field_name, field in six.iteritems(fields):
            # ID is always provided in the root of JSON API so remove it from attributes
            if field_name == 'id':
                continue
            # don't output a key for write only fields
            if fields[field_name].write_only:
                continue
            # Overwite
            # Skip fields with relations
            '''
            if isinstance(
                    field, (relations.RelatedField, relations.ManyRelatedField, BaseSerializer)
            ):
                continue
            '''
            # Skip read_only attribute fields when `resource` is an empty
            # serializer. Prevents the "Raw Data" form of the browsable API
            # from rendering `"foo": null` for read only fields
            try:
                resource[field_name]
            except KeyError:
                if fields[field_name].read_only:
                    continue

            data.update({
                field_name: resource.get(field_name)
            })

        return utils.format_keys(data)

    @classmethod
    def build_json_resource_obj(cls, fields, resource, resource_instance, resource_name,
                                force_type_resolution=False):
        # Determine type from the instance if the underlying model is polymorphic
        if force_type_resolution:
            resource_name = utils.get_resource_type_from_instance(resource_instance)
        resource_data = [
            ('object', resource_name),
            ('id', encoding.force_text(resource_instance.pk) if resource_instance else None),
            # ('attributes', cls.extract_attributes(fields, resource)),
        ]
        attributes = cls.extract_attributes(fields, resource)
        for field, value in attributes.items():
            resource_data.append((field, value))
        # Overwrite
        '''
        relationships = cls.extract_relationships(fields, resource, resource_instance)
        if relationships:
            resource_data.append(('relationships', relationships))
        '''
        # Add 'self' link if field is present and valid
        if api_settings.URL_FIELD_NAME in resource and \
                isinstance(fields[api_settings.URL_FIELD_NAME], relations.RelatedField):
            resource_data.append(('links', {'self': resource[api_settings.URL_FIELD_NAME]}))
        return OrderedDict(resource_data)

    def render_errors(self, data, accepted_media_type=None, renderer_context=None):
        return super(renderers.JSONRenderer, self).render(
            data, accepted_media_type, renderer_context
        )


