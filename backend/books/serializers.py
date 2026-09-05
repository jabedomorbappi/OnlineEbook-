from rest_framework import serializers
from .models import Folder, Book, Page, SkipRule


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'page_number', 'content', 'is_skipped']


class BookListSerializer(serializers.ModelSerializer):
    """Lightweight book representation for directory lists and shelf views."""
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'drive_file_id', 'title', 'total_pages', 'cover_image_url', 'is_processed']

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image and hasattr(obj.cover_image, 'url'):
            return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url
        return None


class BookDetailSerializer(serializers.ModelSerializer):
    """Detailed book representation."""
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'drive_file_id', 'title', 'total_pages', 'cover_image_url', 'is_processed', 'created_at']

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image and hasattr(obj.cover_image, 'url'):
            return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url
        return None


class FolderTreeSerializer(serializers.ModelSerializer):
    """Recursively serializes folders, subfolders, and contained books."""
    subfolders = serializers.SerializerMethodField()
    books = BookListSerializer(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'drive_folder_id', 'name', 'books', 'subfolders']

    def get_subfolders(self, obj):
        # Recursively serialize subfolders
        serializer = FolderTreeSerializer(obj.subfolders.all(), many=True, context=self.context)
        return serializer.data