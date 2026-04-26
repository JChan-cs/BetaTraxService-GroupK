from factory.django import DjangoModelFactory
from factory import SubFactory, Faker
from django.contrib.auth.models import User
from defects.models import DefectReport

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Faker('user_name')
    email = Faker('email')
    password = Faker('password')


class DefectReportFactory(DjangoModelFactory):
    class Meta:
        model = DefectReport

    ProductID = Faker('uuid4')
    Version = Faker('numerify', text='1.#.#')
    ReportTitle = Faker('sentence', nb_words=4)
    Description = Faker('paragraph')
    Steps = Faker('paragraph')
    TesterID = Faker('uuid4')
    Status = 'Assigned'
    assigned_to = SubFactory(UserFactory)