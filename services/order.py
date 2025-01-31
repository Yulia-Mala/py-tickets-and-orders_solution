from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet

from db.models import Ticket, Order


def create_order(tickets: list[dict],
                 username: str,
                 date: str = None) -> Order:
    with transaction.atomic():
        user = get_user_model().objects.get(username=username)
        order = Order.objects.create(user=user)
        if date is not None:
            order.created_at = date
            order.save()
        for ticket in tickets:
            Ticket.objects.create(movie_session_id=ticket["movie_session"],
                                  order=order,
                                  row=ticket["row"],
                                  seat=ticket["seat"])
        return order


def get_orders(username: str = None) -> QuerySet:
    query_set = Order.objects.all()
    if username is not None:
        query_set = query_set.filter(user__username=username)
    return query_set
