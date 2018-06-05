from django.shortcuts import render

# Create your views here.
from .models import Book, Author, BookInstance, Genre
from django.contrib.auth.decorators import login_required

@login_required # For function-based view - sends them to login page, then when they login brings them back to this one
def index(request):
    """
    View function for home page of site.
    """
    
    visits = request.session.get('num_visits',0)#request.session keeps track of interactions with that browser (profile for browser, basically)
                                                #.get is dictionary method (key, default value if no such key found)
    visits +=1
    request.session['num_visits'] = visits #increments every time they visit  
                                        #session ID is stored in browser cookie, actual data is in a database server-side  
    #request.session.modified = True 
    #only saves the session data if it's been modified/deleted - if it hasn't, needs to be specified                                                                            
                                                
    # Generate counts of some of the main objects
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # The 'all()' is implied by default.
    num_genres = Genre.objects.count()
    num_books_with_monkey_in_title=BookInstance.objects.filter(status__icontains='monkey').count()
    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'Index.html',
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors,'num_genres':num_genres, 'num_books_with_monkey_in_title':num_books_with_monkey_in_title,'num_visits':visits},
    )
    
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin # For class-based view - sends them to login page, then when they login brings them back to this one

class BookListView(generic.ListView): #looks for template at templates/catalog/book_list.html
    model = Book
   #queryset = Book.objects.filter(title__icontains='war')[:5] - List displays 5 books containing the title war    
   #template_name = 'books/my_arbitrary_template_name_list.html' - Set custom template location
    paginate_by=2; #2 records per page
    queryset = Book.objects.order_by('title') #has to be a ordering when using pages
      
class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book   
    
class AuthorListView(generic.ListView): 
    model = Author
    paginate_by=2; #2 records per page
    queryset = Author.objects.order_by('last_name') #has to be a ordering when using pages
      
class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author   
    
class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user. 
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html' #Giving this particular bookinstancelist a specific name
    paginate_by = 2
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')#Only gets books borrowed by user and on loan  
        
from django.contrib.auth.mixins import PermissionRequiredMixin #For class-based view - login needs a specific permission to access this

class LoanedBooksListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    """
    Generic class-based view all listing books on loan. 
    """
    permission_required = ('catalog.can_mark_returned', 'catalog.can_mark_maintenance',)#Librarians have access to these
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_all.html' #Giving this particular bookinstancelist a specific name
    paginate_by = 1
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')#Only gets books on loan 
        
from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm

@permission_required('catalog.can_renew')#For function-based view - login needs a specific permission to access this
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data - form is being submitted
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form. - page is being requested
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})        
    
#These auto generate forms and do basic tasks - still need to provide the templates - one for update/create, one for delete    
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('catalog.can_create_author')
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}    

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('catalog.can_change_author')
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']
    
class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('catalog.can_delete_author')
    model = Author
    success_url = reverse_lazy('authors')   
    template_name_suffix = '_delete' # template will be author_delete      
    
class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('catalog.can_create_book')
    model = Book
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}    

class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('catalog.can_change_book')
    model = Book
    fields = '__all__'
    
class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('catalog.can_delete_book')
    model = Book
    success_url = reverse_lazy('books')   
    template_name_suffix = '_delete' # template will be book_delete               
