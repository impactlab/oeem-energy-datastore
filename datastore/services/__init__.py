"""Portal Service Layer

The service layer provides an API on top of Django models to build useful outputs for consumers such as views. This layer helps keep views thin, encourages reusability across views, simplifies testing, and eases separation of concerns for models.

Have a look at this example on SO for a high-level example: http://stackoverflow.com/questions/12578908/separation-of-business-logic-and-data-access-in-django/12579490#12579490


    I usually implement a service layer in between views and models. This acts like your project's API and gives you a good helicopter view of what is going on. I inherited this practice from a colleague of mine that uses this layering technique a lot with Java projects (JSF), e.g:

models.py

    class Book:
       author = models.ForeignKey(User)
       title = models.CharField(max_length=125)

       class Meta:
           app_label = "library"

services.py

    from library.models import Book

    def get_books(limit=None, **filters):
        simple service function for retrieving books can be widely extended
        if limit:
            return Book.objects.filter(**filters)[:limit]
        return Book.objects.filter(**filters)

views.py

    from library.services import get_books

    class BookListView(ListView):
        simple view, e.g. implement a _build and _apply filters function
        queryset = get_books()

"""

from .overview import overview
from .meterruns_export import meterruns_export