import requests
from django.core.cache import cache
from django.core.mail import send_mail, mail_admins, BadHeaderError, EmailMessage
from django.shortcuts import render
from playground.tasks import send_notification_to_customer
from templated_mail.mail import BaseEmailMessage


def say_hello(request):
    # send_notification_to_customer.delay("HELLO")
    try:
        # send_mail("SUBJECT", "Message", "info@kpaul.com", ["bob_mail@kpaul.com"])
        # email = EmailMessage(
        #     "subject",
        #     "message",
        #     "from@kpaul.com",
        #     ["cat@kpaul.com"]
        # )
        # email.attach_file("playground/static/images/dog.jpeg")
        # email.send()

        # message = BaseEmailMessage(
        #     template_name="emails/hello.html",
        #     context={"name": "Kaushik"}
        # )
        # message.send(["bob@kpaul.com"])
        key = "httpbin_result"
        if cache.get(key) is None:
            response = requests.get("https://httpbin.org/delay/2")
            data = response.json()
            cache.set(key, data)

    except BadHeaderError:
        pass
    return render(request, 'hello.html', {'name': cache.get(key)})
