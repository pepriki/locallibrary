from django.db.models import RestrictedError
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView

from .models import Book, Author, BookInstance, Genre, Language

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from catalog.forms import RenewBookForm

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 'num_visits': num_visits},
    )


from django.views import generic


class BookListView(generic.ListView):
    """Generic class-based view for a list of books."""
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = Book

class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""
    model = Author


class GenreDetailView(generic.DetailView):
    """Generic class-based detail view for a genre."""
    model = Genre

class GenreListView(generic.ListView):
    """Generic class-based list view for a list of genres."""
    model = Genre
    paginate_by = 10

class LanguageDetailView(generic.DetailView):
    """Generic class-based detail view for a genre."""
    model = Language

class LanguageListView(generic.ListView):
    """Generic class-based list view for a list of genres."""
    model = Language
    paginate_by = 10

class BookInstanceListView(generic.ListView):
    """Generic class-based view for a list of books."""
    model = BookInstance
    paginate_by = 10

class BookInstanceDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = BookInstance


from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact=BookInstance.LoanStatus.ON_LOAN)
            .order_by('due_back')
        )

from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':

        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date, })

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact=BookInstance.LoanStatus.ON_LOAN).order_by('due_back')


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': datetime.date(2023, 11, 11)}
    permission_required = 'catalog.add_author'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'catalog.change_author'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except RestrictedError:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )

# Classes created for the forms challenge


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.add_book'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.change_book'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.delete_book'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except RestrictedError:
            return HttpResponseRedirect(
                reverse("book-delete", kwargs={"pk": self.object.pk})
            )

class GenreCreate(PermissionRequiredMixin, CreateView):
    model = Genre
    fields = ['name', ]
    permission_required = 'catalog.add_genre'


class GenreUpdate(PermissionRequiredMixin, UpdateView):
    model = Genre
    fields = ['name', ]
    permission_required = 'catalog.change_genre'


class GenreDelete(PermissionRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy('genres')
    permission_required = 'catalog.delete_genre'


class LanguageCreate(PermissionRequiredMixin, CreateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.add_language'


class LanguageUpdate(PermissionRequiredMixin, UpdateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.change_language'


class LanguageDelete(PermissionRequiredMixin, DeleteView):
    model = Language
    success_url = reverse_lazy('languages')
    permission_required = 'catalog.delete_language'


class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    model = BookInstance
    fields = ['book', 'imprint', 'due_back', 'borrower', 'status']
    permission_required = 'catalog.add_bookinstance'


class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    model = BookInstance
    # fields = "__all__"
    fields = ['imprint', 'due_back', 'borrower', 'status']
    permission_required = 'catalog.change_bookinstance'


class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    success_url = reverse_lazy('bookinstances')
    permission_required = 'catalog.delete_bookinstance'