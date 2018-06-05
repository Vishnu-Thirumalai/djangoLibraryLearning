from django.contrib import admin

# Register your models here.
from .models import Author, Genre, Book, BookInstance, Language

#Normal Registration
admin.site.register(Genre)
admin.site.register(Language)

#Adds an admin so the admin website looks different (two different ways of doing it)
class BooksInline(admin.TabularInline):
    model = Book
    extra = 0  # By default display 3 empty slots for adding
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')#Displaying
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]#Editing/Creation
admin.site.register(Author,AuthorAdmin)


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0 # By default display 3 empty slots for adding
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]
@admin.register(BookInstance) 


class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ('status', 'due_back')#Filter main list   
    fieldsets = ( #Sections while editing
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': (('status', 'due_back'),'borrower',)
        }),
     )   
    
