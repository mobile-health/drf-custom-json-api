# -*- coding: utf-8 -*-
import collections
import re
import os
import sys
import six
import copy

from rest_framework.views import exception_handler as default_django_rest_exception  # NOQA
from raven.contrib.django.raven_compat.models import sentry_exception_handler
from rest_framework.response import Response
from rest_framework_friendly_errors.handlers import *


ERROR_DATA_FORMAT = {
    'request_id': '',
    'code': 400,
    'message': "",
    'errors': []
}

try:
    from log_request_id import local
    ERROR_DATA_FORMAT['request_id'] = local.request_id
except Exception as e:
    pass

VALIDATE_ERROR_ITEM = {
    'field': "",
    'message': ""
}


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in six.iteritems(d):
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(six.iteritems(flatten(v, new_key, sep=sep)))
        else:
            items.append((new_key, v))
    return dict(items)


def replace_dot_without_decimal(msg):
    p = re.compile("(?<=\d)(\.)(?!\d)")
    return p.sub("", str(msg))


def sanitize_message(msg):
    if isinstance(msg, list):
        msg = u'. '.join(replace_dot_without_decimal(v) for v in msg)
    else:
        msg = replace_dot_without_decimal(msg)
    return str(msg)


def get_message_from_errors(errors):

    if isinstance(errors, dict):
        errors = flatten(errors)
        errors = errors.values()
    return u'. '.join(sanitize_message(v) for v in errors)


def get_validate_errors(errors):
    error_data = []
    try:
        for k, v in errors.items():
            error_item = copy.copy(VALIDATE_ERROR_ITEM)
            error_item["field"] = k
            error_item["message"] = v[0]
            error_data.append(error_item)
    except Exception:
        pass
    return error_data


def get_error_data(status_code, errors, exc):
    error_data = ERROR_DATA_FORMAT
    error_data["code"] = 0
    error_data["message"] = get_message_from_errors(errors)
    error_data["errors"] = get_validate_errors(errors)
    return error_data


def custom_exception_handler(exc, context):
    TESTING_MODE = os.path.basename(sys.argv[0]) in ('pytest', 'py.test')
    if not TESTING_MODE and context.get('request'):
        sentry_exception_handler(request=context["request"])
    response = default_django_rest_exception(exc, context)

    if response is None:
        return response
    error_data = get_error_data(response.status_code, response.data, exc)
    response.data = error_data
    return response
