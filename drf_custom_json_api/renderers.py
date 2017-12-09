from rest_framework_json_api import renderers


class JSONRenderer(renderers.JSONRenderer):

    def render_errors(self, data, accepted_media_type=None, renderer_context=None):
        return super(renderers.JSONRenderer, self).render(
            data, accepted_media_type, renderer_context
        )

