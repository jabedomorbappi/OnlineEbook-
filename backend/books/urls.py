from django.urls import path
from .views import DirectoryTreeView, BookDetailView, BookPageDetailView

urlpatterns = [
    path('tree/', DirectoryTreeView.as_view(), name='directory-tree'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/<int:book_id>/page/<int:page_number>/', BookPageDetailView.as_view(), name='book-page-detail'),
]