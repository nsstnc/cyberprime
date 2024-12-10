from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class GoogleDrive:
    def __init__(self, client_secret_filepath):
        # Аутентификация и создание клиента gspread
        scope = ["https://www.googleapis.com/auth/drive"]
        credentials = service_account.Credentials.from_service_account_file(
            client_secret_filepath, scopes=scope)
        self.client = build('drive', 'v3', credentials=credentials)

    def upload_file_to_drive(self, file_path, file_name):
        """Загружает файл в Google Drive и возвращает публичный URL."""
        # Загружаем файл
        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_path, resumable=True)
        file = self.client.files().create(body=file_metadata, media_body=media, fields='id').execute()

        # Устанавливаем публичный доступ
        file_id = file.get('id')
        self.client.permissions().create(fileId=file_id, body={'role': 'reader', 'type': 'anyone'}).execute()

        # Получаем публичный URL
        public_url = f"https://drive.google.com/uc?id={file_id}"
        return public_url
