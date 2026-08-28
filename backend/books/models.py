from django.db import models

# Create your models here.
class Folder(models.Model):
    """
    Mirrors a folder in Google Drive. Groups related books self-referancing parent supports nested drive folder stures

    Args:
        models (_type_): _description_
    """
    
    name=models.CharField(max_length=255)
    drive_folder_id=models.CharField(max_length=255,unique=True)
    parent=models.ForeignKey(
        'self',null=True,blank=True,on_delete=models.CASCADE,related_name='subfolders'
    )
    
    def __str__(self):
        return self.name 
    
    
class Book(models.Model):
    """
    One PDF from Drive = one Book. We don't keep the PDF file long-term —
    just metadata + a link to its extracted Pages.
    """
    
    title=models.CharField(max_length=500)
    drive_file_id=models.CharField(max_length=255,unique=True)
    folder=models.ForeignKey(
        Folder,on_delete=models.CASCADE,related_name='books'
    )
    total_pages=models.PositiveBigIntegerField(default=0)
    is_processed=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    
class Page(models.Model):
    """
    One extracted page of a book's text. Kept as its own table (not a
    field on Book) so the API can fetch exactly one page at a time —
    this is what makes true 'page by page' reading possible, instead of
    loading the whole book into one response.
    """
    
    
    book=models.ForeignKey(Book,on_delete=models.CASCADE,related_name='pages')
    page_number=models.PositiveBigIntegerField()
    content=models.TextField()
    is_skipped=models.BooleanField(
        default=False,
        help_text="If True, excluded from the reading flow"
    )
    
    class Meta:
        unique_together=("book","page_number")
        ordering=['page_number']
    def __str__(self):
        return f"{self.book.title} -page {self.page_number}"   
        
class SkipRule(models.Model):
    """
    Defines what to exclude when processing a book (e.g. 'skip pages 1-2'
    for cover/blank pages, or 'skip 250-260' for references/index).
    Applied during PDF processing — skipped content never becomes a
    Page row, so nothing extra is needed at read-time.
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='skip_rules')
    start_page = models.PositiveIntegerField()
    end_page = models.PositiveIntegerField()
    reason = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.book.title}: skip {self.start_page}-{self.end_page}"        