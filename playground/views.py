from django.shortcuts import render
from playground.tasks import send_notification_to_customer


def say_hello(request):
    send_notification_to_customer.delay("HELLO")
    return render(request, 'hello.html', {'name': 'Mosh'})
