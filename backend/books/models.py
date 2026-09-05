from django.db import models


class Folder(models.Model):
    """
    Mirrors a folder in Google Drive. Groups related books self-referencing 
    parent supports nested drive folder structures.
    """
    name = models.CharField(max_length=255)
    drive_folder_id = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='subfolders'
    )

    def __str__(self):
        return self.name 


class Book(models.Model):
    """
    One PDF from Drive = one Book. Stores metadata, cover image, and links to Page objects.
    """
    title = models.CharField(max_length=500)
    drive_file_id = models.CharField(max_length=255, unique=True)
    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, related_name='books'
    )
    total_pages = models.PositiveBigIntegerField(default=0)
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Page(models.Model):
    """
    One extracted page of a book's text.
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='pages')
    page_number = models.PositiveBigIntegerField()
    content = models.TextField()
    is_skipped = models.BooleanField(
        default=False,
        help_text="If True, excluded from the reading flow"
    )

    class Meta:
        unique_together = ("book", "page_number")
        ordering = ['page_number']

    def __str__(self):
        return f"{self.book.title} - page {self.page_number}"


class SkipRule(models.Model):
    """
    Defines what to exclude when processing a book.
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='skip_rules')
    start_page = models.PositiveIntegerField()
    end_page = models.PositiveIntegerField()
    reason = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.book.title}: skip {self.start_page}-{self.end_page}"