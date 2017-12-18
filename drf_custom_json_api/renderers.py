from __future__ import unicode_literals

from rest_framework_json_api import utils
from rest_framework_json_api import renderers
from collections import OrderedDict
from rest_framework import relations
from django.utils import encoding, six
from rest_framework.settings import api_settings
from rest_framework.serializers import BaseSerializer, ListSerializer, Serializer


class JSONRenderer(renderers.JSONRenderer):
    @classmethod
    def build_json_resource_obj(cls, fields, resource, resource_instance, resource_name,
                                force_type_resolution=False):
        # Determine type from the instance if the underlying model is polymorphic
        if force_type_resolution:
            resource_name = utils.get_resource_type_from_instance(resource_instance)
        resource_data = [
            ('object', resource_name),
            ('id', resource_instance.pk if resource_instance else None),
        ]
        attributes = cls.extract_attributes(fields, resource)
        for field, value in attributes.items():
            resource_data.append((field, value))

        relationships = cls.extract_relationships(fields, resource, resource_instance)
        for field, value in relationships.items():
            resource_data.append((field, value))
        # if relationships:
        #    resource_data.append(('relationships', relationships))

        # Add 'self' link if field is present and valid
        if api_settings.URL_FIELD_NAME in resource and \
                isinstance(fields[api_settings.URL_FIELD_NAME], relations.RelatedField):
            resource_data.append(('links', {'self': resource[api_settings.URL_FIELD_NAME]}))
        return OrderedDict(resource_data)

    @classmethod
    def extract_relationships(cls, fields, resource, resource_instance):
        # Avoid circular deps
        from rest_framework_json_api.relations import ResourceRelatedField

        data = OrderedDict()

        # Don't try to extract relationships from a non-existent resource
        if resource_instance is None:
            return

        for field_name, field in six.iteritems(fields):
            # Skip URL field
            if field_name == api_settings.URL_FIELD_NAME:
                continue

            # Skip fields without relations
            if not isinstance(
                    field, (relations.RelatedField, relations.ManyRelatedField, BaseSerializer)
            ):
                continue

            source = field.source
            relation_type = utils.get_related_resource_type(field)

            if isinstance(field, relations.HyperlinkedIdentityField):
                resolved, relation_instance = utils.get_relation_instance(
                    resource_instance, source, field.parent
                )
                if not resolved:
                    continue
                # special case for HyperlinkedIdentityField
                relation_data = list()

                # Don't try to query an empty relation
                relation_queryset = relation_instance \
                    if relation_instance is not None else list()

                for related_object in relation_queryset:
                    relation_data.append(
                        OrderedDict([
                            ('object', relation_type),
                            ('id', encoding.force_text(related_object.pk))
                        ])
                    )

                data.update({field_name: {
                    'links': {
                        "related": resource.get(field_name)},
                    'data': relation_data,
                    'meta': {
                        'count': len(relation_data),
                        'include': []
                    }
                }})
                continue

            if isinstance(field, ResourceRelatedField):
                resolved, relation_instance = utils.get_relation_instance(
                    resource_instance, source, field.parent
                )
                if not resolved:
                    continue

                # special case for ResourceRelatedField
                relation_data = {
                    'data': resource.get(field_name),
                    'meta': {
                        'include': []
                    }
                }

                field_links = field.get_links(
                    resource_instance, field.related_link_lookup_field)
                relation_data.update(
                    {'links': field_links}
                    if field_links else dict()
                )
                data.update({field_name: relation_data})
                continue

            if isinstance(
                    field, (relations.PrimaryKeyRelatedField, relations.HyperlinkedRelatedField)
            ):
                resolved, relation = utils.get_relation_instance(
                    resource_instance, '%s_id' % source, field.parent
                )
                if not resolved:
                    continue
                relation_id = relation if resource.get(field_name) else None
                relation_data = {
                    'data': (
                        OrderedDict([
                            ('object', relation_type), ('id', encoding.force_text(relation_id))
                        ])
                        if relation_id is not None else None),
                    'meta': {
                        'include': []
                    }
                }

                if (
                            isinstance(field, relations.HyperlinkedRelatedField) and
                            resource.get(field_name)
                ):
                    relation_data.update(
                        {
                            'links': {
                                'related': resource.get(field_name)
                            }
                        }
                    )
                data.update({field_name: relation_data})
                continue

            if isinstance(field, relations.ManyRelatedField):
                resolved, relation_instance = utils.get_relation_instance(
                    resource_instance, source, field.parent
                )
                if not resolved:
                    continue

                if isinstance(field.child_relation, ResourceRelatedField):
                    # special case for ResourceRelatedField
                    relation_data = {
                        'data': resource.get(field_name)
                    }

                    field_links = field.child_relation.get_links(
                        resource_instance,
                        field.child_relation.related_link_lookup_field
                    )
                    relation_data.update(
                        {'links': field_links}
                        if field_links else dict()
                    )
                    relation_data.update(
                        {
                            'meta': {
                                'count': len(resource.get(field_name)),
                                'include': []
                            }
                        }
                    )
                    data.update({field_name: relation_data})
                    continue

                relation_data = list()
                for nested_resource_instance in relation_instance:
                    nested_resource_instance_type = (
                        relation_type or
                        utils.get_resource_type_from_instance(nested_resource_instance)
                    )

                    nested_data = OrderedDict([
                        ('object', nested_resource_instance_type),
                        ('id', nested_resource_instance.id)
                    ])
                    # nested_data.update(resource.get(field_name))

                    relation_data.append(nested_data)

                data.update({
                    field_name: {
                        'data': relation_data,
                        'meta': {
                            'count': len(relation_data),
                            'include': []
                        }
                    }
                })
                continue

            if isinstance(field, ListSerializer):
                resolved, relation_instance = utils.get_relation_instance(
                    resource_instance, source, field.parent
                )
                if not resolved:
                    continue

                relation_data = list()

                serializer_data = resource.get(field_name)
                resource_instance_queryset = list(relation_instance)
                if isinstance(serializer_data, list):
                    for position in range(len(serializer_data)):
                        nested_resource_instance = resource_instance_queryset[position]
                        nested_resource_instance_type = (
                            relation_type or
                            utils.get_resource_type_from_instance(nested_resource_instance)
                        )
                        nested_data = OrderedDict([
                            ('object', nested_resource_instance_type),
                        ])
                        nested_data.update(serializer_data[position])

                        relation_data.append(nested_data)

                    data.update({
                        field_name: {
                            'data': relation_data,
                            'meta': {
                                'include': []
                            }
                        }
                    })
                    continue

            if isinstance(field, Serializer):
                resolved, relation_instance = utils.get_relation_instance(
                    resource_instance, source, field.parent
                )
                if not resolved:
                    continue

                relation_data = None
                serializer_data = resource.get(field_name)
                if serializer_data:
                    relation_data = OrderedDict([
                        ('object', relation_type),
                    ])
                    relation_data.update(serializer_data)

                data.update({
                    field_name: {
                        'data': relation_data,
                        'meta': {
                            'include': []
                        }
                    }
                })
                continue

        return utils.format_keys(data)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        view = renderer_context.get("view", None)
        request = renderer_context.get("request", None)

        # Get the resource name.
        resource_name = utils.get_resource_name(renderer_context)

        # If this is an error response, skip the rest.
        if resource_name == 'errors':
            return self.render_errors(data, accepted_media_type, renderer_context)

        # if response.status_code is 204 then the data to be rendered must
        # be None
        response = renderer_context.get('response', None)
        if response is not None and response.status_code == 204:
            return super(JSONRenderer, self).render(
                None, accepted_media_type, renderer_context
            )

        from rest_framework_json_api.views import RelationshipView
        if isinstance(view, RelationshipView):
            return self.render_relationship_view(data, accepted_media_type, renderer_context)

        # If `resource_name` is set to None then render default as the dev
        # wants to build the output format manually.
        if resource_name is None or resource_name is False:
            return super(JSONRenderer, self).render(
                data, accepted_media_type, renderer_context
            )

        json_api_data = data
        json_api_included = list()
        # initialize json_api_meta with pagination meta or an empty dict
        json_api_meta = data.get('meta', {}) if isinstance(data, dict) else {}
        json_api_meta['include'] = []
        json_api_meta['custom'] = []

        if data and 'results' in data:
            serializer_data = data["results"]
        else:
            serializer_data = data

        serializer = getattr(serializer_data, 'serializer', None)

        included_resources = utils.get_included_resources(request, serializer)

        if serializer is not None:

            # Get the serializer fields
            fields = utils.get_serializer_fields(serializer)

            # Determine if resource name must be resolved on each instance (polymorphic serializer)
            force_type_resolution = getattr(serializer, '_poly_force_type_resolution', False)

            # Extract root meta for any type of serializer
            json_api_meta.update(self.extract_root_meta(serializer, serializer_data))

            if getattr(serializer, 'many', False):
                json_api_data = list()

                for position in range(len(serializer_data)):
                    resource = serializer_data[position]  # Get current resource
                    resource_instance = serializer.instance[position]  # Get current instance

                    json_resource_obj = self.build_json_resource_obj(
                        fields, resource, resource_instance, resource_name, force_type_resolution
                    )
                    meta = self.extract_meta(serializer, resource)
                    if meta:
                        json_resource_obj.update({'meta': utils.format_keys(meta)})
                    json_api_data.append(json_resource_obj)

                    included = self.extract_included(
                        fields, resource, resource_instance, included_resources
                    )
                    if included:
                        json_api_included.extend(included)
            else:
                resource_instance = serializer.instance
                json_api_data = self.build_json_resource_obj(
                    fields, serializer_data, resource_instance, resource_name, force_type_resolution
                )

                meta = self.extract_meta(serializer, serializer_data)
                if meta:
                    json_api_data.update({'meta': utils.format_keys(meta)})

                included = self.extract_included(
                    fields, serializer_data, resource_instance, included_resources
                )
                if included:
                    json_api_included.extend(included)

        # Make sure we render data in a specific order
        render_data = OrderedDict()

        if isinstance(data, dict) and data.get('links'):
            render_data['links'] = data.get('links')

        # format the api root link list
        if view.__class__ and view.__class__.__name__ == 'APIRoot':
            render_data['data'] = None
            render_data['links'] = json_api_data
        else:
            render_data['data'] = json_api_data

        if len(json_api_included) > 0:
            # Iterate through compound documents to remove duplicates
            seen = set()
            unique_compound_documents = list()
            for included_dict in json_api_included:
                type_tuple = tuple((included_dict['type'], included_dict['id']))
                if type_tuple not in seen:
                    seen.add(type_tuple)
                    unique_compound_documents.append(included_dict)

            # Sort the items by type then by id
            render_data['included'] = sorted(
                unique_compound_documents, key=lambda item: (item['type'], item['id'])
            )

        if json_api_meta:
            render_data['meta'] = utils.format_keys(json_api_meta)

        return super(renderers.JSONRenderer, self).render(
            render_data, accepted_media_type, renderer_context
        )
