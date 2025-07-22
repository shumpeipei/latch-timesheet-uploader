import requests
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from googleapiclient.discovery import build
import re
import json

# 設定ファイルからスプレッドシートファイルパスを読み込む
with open("./config.json", encoding="utf-8") as config_file:
    config = json.load(config_file)
    spreadsheet_file_path = config["spreadsheet_file_path"]
    service_account_file_path = config["service_account_file_path"]

# 認証情報ファイルとスコープ
SERVICE_ACCOUNT_FILE = service_account_file_path
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# 認証処理
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
authed_session = AuthorizedSession(credentials)

# スプレッドシートID（URL中の「/d/xxxxxxx/」部分）
# JSONファイルからスプレッドシートIDを取得
with open(spreadsheet_file_path, 'r', encoding='utf-8') as f:
    file_list = json.load(f)

# 最初のファイルの fileId を使用
spreadsheet_id = file_list[0]['fileId']

# Sheets API を使ってスプレッドシートの名前を取得
sheets_service = build('sheets', 'v4', credentials=credentials)

# 各スプレッドシートをループで処理
for file in file_list:
    spreadsheet_id = file['fileId']

    try:
        spreadsheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        spreadsheet_title = spreadsheet_metadata.get('properties', {}).get('title', 'spreadsheet')
        # ファイル名として使えない文字を除去（安全のため）
        safe_title = re.sub(r'[\\/*?:"<>|]', '_', spreadsheet_title)
        filename = f"{safe_title}.pdf"

        # PDFエクスポートURL（パラメータ調整可能）
        export_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=pdf&portrait=true&size=A4&sheetnames=false&printtitle=false&pagenumbers=false&gridlines=false&fzr=false'

        # PDFを取得してローカルに保存
        response = authed_session.get(export_url)
        # Content-Type をチェック
        if response.headers.get("Content-Type") == "application/pdf":
            with open(filename, 'wb') as f:
                f.write(response.content)
                print("PDFとして保存されました")
        else:
            print("PDFではなくHTML等が返されました")
            print("Content-Type:", response.headers.get("Content-Type"))
            print("レスポンス冒頭:", response.text[:300]) 

    except Exception as e:
        print(f"処理失敗: {file.get('fileName', '不明なファイル')}")
        print("エラー内容:", str(e))