from rest_framework_json_api.pagination import *
from django.core.paginator import InvalidPage


class CustomPageNumberPagination(PageNumberPagination):

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
                ('total', self.page.paginator.count),
                ('first', self.build_link(1)),
                ('last', self.build_link(self.page.paginator.num_pages)),
                ('next', self.build_link(next)),
                ('prev', self.build_link(previous))
            ])
        })

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            self.request = request
            self.page = paginator.page(paginator.num_pages)
            return list()

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)


class PageNumberPagination(PageNumberPagination):

    def get_paginated_response(self, data):
        next = None
        previous = None

        if self.page.has_next():
            next = self.page.next_page_number()
        if self.page.has_previous():
            previous = self.page.previous_page_number()

        return Response({
            'results': data,
            'meta': {
                'pagination': OrderedDict([
                    ('page', self.page.number),
                    ('pages', self.page.paginator.num_pages),
                    ('count', self.page.paginator.count),
                ]),
                'links': OrderedDict([
                    ('first', self.build_link(1)),
                    ('last', self.build_link(self.page.paginator.num_pages)),
                    ('next', self.build_link(next)),
                    ('prev', self.build_link(previous))
                ])
            }
        })
