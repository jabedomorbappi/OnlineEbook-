from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Folder, Book, Page
from .serializers import (
    FolderTreeSerializer,
    BookDetailSerializer,
    BookListSerializer,
    PageSerializer
)


class DirectoryTreeView(APIView):
    """
    Returns the entire folder tree starting from root folders (folders with no parent).
    """
    def get(self, request):
        root_folders = Folder.objects.filter(parent__isnull=True)
        serializer = FolderTreeSerializer(root_folders, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookDetailView(generics.RetrieveAPIView):
    """Fetch metadata for a single book."""
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer


class BookPageDetailView(APIView):
    """
    Fetch a single page of a book by page number.
    URL format: /api/books/<book_id>/page/<page_number>/
    """
    def get(self, request, book_id, page_number):
        page = get_object_or_404(
            Page.objects.select_related('book'),
            book_id=book_id,
            page_number=page_number
        )
        serializer = PageSerializer(page)
        return Response(serializer.data, status=status.HTTP_200_OK)