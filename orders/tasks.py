from celery import shared_task
from django.core.mail import send_mail
from .models import Order


@shared_task
def order_created(order_id):
    order = Order.objects.get(id=order_id)
    subject = 'Zamówienie nr {}'.format(order.id)
    message = 'Witaj, {}!\n\nZłożyłeś zamówienie w naszym sklepie. Identyfikator zamówienia to {}.'.format(order.first_name, order.id)
    mail_sent = send_mail(subject, message, 'pawel.florczak87@gmail.com', [order.email])

    return mail_sent
