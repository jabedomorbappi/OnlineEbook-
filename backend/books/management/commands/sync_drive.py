import os
from django.core.management.base import BaseCommand
# Changed drive_sync to drive_client
from books.services.drive_client import DriveProcessor


class Command(BaseCommand):
    help = "Sync Google Drive folder tree, extract covers, and save pages to database"

    def handle(self, *args, **options):
        root_folder_id = os.getenv('DRIVE_ROOT_FOLDER_ID', '1a9vGTIxoJsOdxFkHiy0xiGVS6DJjQYzz')

        self.stdout.write(self.style.NOTICE("Starting Google Drive synchronization..."))
        
        processor = DriveProcessor()
        processor.sync_drive(root_folder_id)

        self.stdout.write(self.style.SUCCESS("Successfully synchronized Google Drive data!"))