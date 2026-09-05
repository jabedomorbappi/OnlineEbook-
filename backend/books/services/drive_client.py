import io
import os
import pymupdf
from dotenv import load_dotenv
from django.core.files.base import ContentFile
from google.oauth2 import service_account
from googleapiclient.discovery import build

from books.models import Folder, Book, Page, SkipRule

# Load variables from .env if present
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


class DriveProcessor:
    def __init__(self):
        # Fallback to local secrets path if environment variable is missing
        default_path = 'secrets/studious-pen-263112-0c234c92f503.json'
        key_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', default_path)

        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Service account file not found at: {key_path}")

        credentials = service_account.Credentials.from_service_account_file(
            key_path, scopes=SCOPES
        )
        self.service = build('drive', 'v3', credentials=credentials)

    def list_subfolders(self, parent_id):
        query = f"'{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        return results.get('files', [])

    def list_pdfs(self, folder_id):
        query = f"'{folder_id}' in parents and mimeType = 'application/pdf' and trashed = false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        return results.get('files', [])

    def download_bytes(self, file_id):
        return self.service.files().get_media(fileId=file_id).execute()

    def process_and_save_book(self, pdf_bytes, book):
        """
        Renders page 1 to a PNG cover, extracts text per page,
        applies skip rules, and bulk-inserts Page objects.
        """
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        book.total_pages = len(doc)
        # ADD THIS LINE HERE:
        print(f"Processing book: {book.title} ({len(doc)} pages)...")

        # 1. Render First Page as Cover Image
        if len(doc) > 0:
            first_page = doc.load_page(0)
            pix = first_page.get_pixmap(dpi=150)
            cover_png_bytes = pix.tobytes("png")
            image_name = f"cover_{book.drive_file_id}.png"
            book.cover_image.save(image_name, ContentFile(cover_png_bytes), save=False)

        # 2. Retrieve active skip ranges for this book
        skip_rules = SkipRule.objects.filter(book=book)
        skip_ranges = [(rule.start_page, rule.end_page) for rule in skip_rules]

        # 3. Process Pages
        page_objects = []
        for index, page in enumerate(doc):
            page_num = index + 1
            is_skipped = any(start <= page_num <= end for start, end in skip_ranges)
            
            text_content = page.get_text() or ""

            page_objects.append(
                Page(
                    book=book,
                    page_number=page_num,
                    content=text_content,
                    is_skipped=is_skipped
                )
            )

        # 4. Bulk create pages and update processing status
        Page.objects.bulk_create(page_objects, ignore_conflicts=True)

        book.is_processed = True
        book.save()

    def sync_drive(self, drive_folder_id, parent_db_folder=None):
        """Recursively syncs Drive folders and processes PDF books into DB."""
        folder_info = self.service.files().get(fileId=drive_folder_id, fields="name").execute()
        
        print(f"Syncing folder: {folder_info['name']}")
        db_folder, _ = Folder.objects.get_or_create(
            drive_folder_id=drive_folder_id,
            defaults={'name': folder_info['name'], 'parent': parent_db_folder}
        )

        # Sync PDFs in current folder
        pdfs = self.list_pdfs(drive_folder_id)
        for pdf in pdfs:
            title = pdf['name'].rsplit('.', 1)[0]
            book, created = Book.objects.get_or_create(
                drive_file_id=pdf['id'],
                defaults={'title': title, 'folder': db_folder}
            )

            if not book.is_processed:
                pdf_bytes = self.download_bytes(pdf['id'])
                self.process_and_save_book(pdf_bytes, book)

        # Recurse subfolders
        subfolders = self.list_subfolders(drive_folder_id)
        for sub in subfolders:
            self.sync_drive(sub['id'], parent_db_folder=db_folder)