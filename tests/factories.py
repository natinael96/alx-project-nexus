"""
Factory classes for creating test data using factory_boy.
"""
import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.models import User
from apps.jobs.models import Category, Job, Application

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances."""
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = 'user'
    is_active = True
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or 'testpass123'
        self.set_password(password)
        self.save()


class EmployerFactory(UserFactory):
    """Factory for creating Employer instances."""
    role = 'employer'
    username = factory.Sequence(lambda n: f'employer{n}')


class AdminFactory(UserFactory):
    """Factory for creating Admin instances."""
    role = 'admin'
    username = factory.Sequence(lambda n: f'admin{n}')
    is_staff = True
    is_superuser = True


class CategoryFactory(factory.django.DjangoModelFactory):
    """Factory for creating Category instances."""
    class Meta:
        model = Category
        django_get_or_create = ('name',)
    
    name = factory.Sequence(lambda n: f'Category {n}')
    description = factory.Faker('text', max_nb_chars=200)
    slug = factory.LazyAttribute(lambda obj: f'category-{obj.name.lower().replace(" ", "-")}')


class JobFactory(factory.django.DjangoModelFactory):
    """Factory for creating Job instances."""
    class Meta:
        model = Job
    
    title = factory.Faker('job')
    description = factory.Faker('text', max_nb_chars=500)
    requirements = factory.Faker('text', max_nb_chars=300)
    category = factory.SubFactory(CategoryFactory)
    employer = factory.SubFactory(EmployerFactory)
    location = factory.Faker('city')
    job_type = 'full-time'
    salary_min = factory.Faker('random_int', min=50000, max=100000)
    salary_max = factory.LazyAttribute(lambda obj: obj.salary_min + 20000)
    status = 'active'
    is_featured = False


class ApplicationFactory(factory.django.DjangoModelFactory):
    """Factory for creating Application instances."""
    class Meta:
        model = Application
    
    job = factory.SubFactory(JobFactory)
    applicant = factory.SubFactory(UserFactory)
    cover_letter = factory.Faker('text', max_nb_chars=500)
    resume = factory.django.FileField(filename='resume.pdf')
    status = 'pending'
