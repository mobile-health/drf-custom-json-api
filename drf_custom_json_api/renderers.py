from __future__ import unicode_literals

from rest_framework_json_api import utils
from rest_framework import renderers
from collections import OrderedDict


class JSONRenderer(renderers.JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        view = renderer_context.get("view", None)
        request = renderer_context.get("request", None)

        # Get the resource name.
        resource_name = utils.get_resource_name(renderer_context)

        if resource_name == 'errors':
            return super(JSONRenderer, self).render(
                data, accepted_media_type, renderer_context
            )

        # if response.status_code is 204 then the data to be rendered must
        # be None
        response = renderer_context.get('response', None)
        if response is not None and response.status_code == 204:
            return super(JSONRenderer, self).render(
                None, accepted_media_type, renderer_context
            )

        # If `resource_name` is set to None then render default as the dev
        # wants to build the output format manually.
        if resource_name is None or resource_name is False:
            return super(JSONRenderer, self).render(
                data, accepted_media_type, renderer_context
            )

        # Make sure we render data in a specific order
        render_data = OrderedDict()

        #json_api_data = data
        json_api_included = list()
        # initialize json_api_meta with pagination meta or an empty dict


        if data and 'results' in data:
            json_api_data = data["results"]
        else:
            json_api_data = data

        json_api_meta = data.get('meta', {}) if isinstance(data, dict) else {}
        json_api_meta['custom'] = []
        #json_api_meta['include'] = json_api_data.keys()
        print(type(json_api_data))

        render_data['data'] = json_api_data
        render_data['meta'] = json_api_meta
        return super(JSONRenderer, self).render(
            render_data, accepted_media_type, renderer_context
        )

