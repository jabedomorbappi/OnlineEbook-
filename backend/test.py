from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']
# Used forward slashes to avoid backslash escape warnings
SERVICE_ACCOUNT_FILE = 'backend\secrets\studious-pen-263112-0c234c92f503.json'
FOLDER_ID = '1a9vGTIxoJsOdxFkHiy0xiGVS6DJjQYzz'

try:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed = false",
        fields="files(id, name)"
    ).execute()
    files = results.get('files', [])
    
    # Replaced emojis with standard text to avoid Windows encoding errors
    print("[SUCCESS] Connection Successful! Access Granted.")
    print(f"Files found in folder: {len(files)}")
    for f in files:
        print(f" - {f['name']}")

except Exception as e:
    print("[ERROR] Permission Error / Access Denied:")
    print(e)