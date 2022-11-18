import json

from django.http.response import HttpResponseRedirect, JsonResponse


def init_response(response_string=None, data=None, response_code=None):
    """
    Initializes the response object
    both arguments are optional.
    """

    response = {"response_code": 1, "response_string": "", "response_data": {}}
    if response_string is not None:
        response["response_string"] = response_string
    if data is not None:
        response["response_data"] = data
    if response_code is not None:
        response["response_code"] = response_code

    return response


def _send(data, status_code):
    return JsonResponse(data=data, status=status_code)


def send_200(data, response_string=""):
    if response_string:
        data["response_string"] = response_string
    return _send(data, 200)


def send_201(data):
    return _send(data, 201)


def send_204(data):
    return _send(data, 204)


def send_302(url):
    return HttpResponseRedirect(url)


def send_400(data, response_string="", response_code=None):
    if response_string:
        data["response_string"] = response_string
    if response_code is not None:
        data["response_code"] = response_code
    return _send(data, 400)


def send_401(data):
    return _send(data, 401)


def send_status_code(data, status_code):
    return _send(data, status_code)


def send_403(data):
    return _send(data, 403)


def send_404(data, response_string=""):
    if response_string:
        data["response_string"] = response_string
    return _send(data, 404)


def send_410(data):
    return _send(data, 410)


def send_500(data):
    return _send(data, 500)


def send_502(data):
    return _send(data, 502)
