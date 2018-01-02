from rest_framework_json_api.pagination import *


class PageNumberPagination(PageNumberPagination):


    def get_paginated_response(self, data):
        next = None
        previous = None

        if self.page.has_next():
            next = self.page.next_page_number()
        if self.page.has_previous():
            previous = self.page.previous_page_number()

        return Response({
            'data': data,
            'pagination': OrderedDict([
                ('page', self.page.number),
                ('pages', self.page.paginator.num_pages),
                ('count', self.page.paginator.count),
                ('first', self.build_link(1)),
                ('last', self.build_link(self.page.paginator.num_pages)),
                ('next', self.build_link(next)),
                ('prev', self.build_link(previous))
            ])
        })



