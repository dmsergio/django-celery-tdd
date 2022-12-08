from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from factory import LazyAttribute
from factory.django import DjangoModelFactory
from factory import Faker


class UserFactory(DjangoModelFactory):
    username = Faker("user_name")
    email = LazyAttribute(lambda o: f"{o.username}@example.com")
    password = LazyAttribute(lambda o: make_password(o.username))
    first_name = Faker("first_name")
    last_name = Faker("last_name")

    class Meta:
        model = User
