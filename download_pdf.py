import os
import sys
import re
import json
from datetime import datetime
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from googleapiclient.discovery import build

CONFIG_FILE_PATH = "./config.json"

if not os.path.exists(CONFIG_FILE_PATH):
    print(f"エラー: 設定ファイルが見つかりません: {CONFIG_FILE_PATH}")
    sys.exit(1)

# 設定ファイルから読み込む
with open(CONFIG_FILE_PATH, encoding="utf-8") as config_file:
    config = json.load(config_file)

service_account_file_path = config.get("service_account_file_path")
if not service_account_file_path or not os.path.exists(service_account_file_path):
    print(f"エラー: サービスアカウント認証ファイルが見つかりません: {service_account_file_path}")
    sys.exit(1)

# 認証情報ファイルとスコープ
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
credentials = service_account.Credentials.from_service_account_file(
    service_account_file_path, scopes=SCOPES
)
authed_session = AuthorizedSession(credentials)

file_list = []

# 1. Drive親フォルダIDから検索する場合
drive_folder_id = config.get("drive_folder_id")
spreadsheet_file_path = config.get("spreadsheet_file_path")

if drive_folder_id:
    drive_service = build('drive', 'v3', credentials=credentials)
    now = datetime.now()
    upload_file_paths = config.get("upload_file_path", [])

    if upload_file_paths:
        # upload_file_pathに定義されたタイトルと完全一致するスプレッドシートを検索
        for path in upload_file_paths:
            resolved_path = path.replace("YYYY", now.strftime("%Y")).replace("MM", now.strftime("%m"))
            expected_title = os.path.splitext(os.path.basename(resolved_path))[0]

            query = (
                f"'{drive_folder_id}' in parents and "
                f"name = '{expected_title}' and "
                f"mimeType = 'application/vnd.google-apps.spreadsheet' and "
                f"trashed = false"
            )
            res = drive_service.files().list(q=query, fields="files(id, name)").execute()
            items = res.get('files', [])

            if not items:
                print(f"エラー: 指定されたスプレッドシートが見つかりませんでした: '{expected_title}' (フォルダID: {drive_folder_id})")
                sys.exit(1)

            file_list.append({
                'fileId': items[0]['id'],
                'fileName': items[0]['name']
            })
    else:
        # 当月年月を含むスプレッドシートを親フォルダから検索
        target_ym = f"{now.strftime('%Y')}年{now.strftime('%m')}月"
        query = (
            f"'{drive_folder_id}' in parents and "
            f"name contains '{target_ym}' and "
            f"mimeType = 'application/vnd.google-apps.spreadsheet' and "
            f"trashed = false"
        )
        res = drive_service.files().list(q=query, fields="files(id, name)", orderBy="name").execute()
        for item in res.get('files', []):
            file_list.append({
                'fileId': item['id'],
                'fileName': item['name']
            })

elif spreadsheet_file_path:
    # 従来互換: 指定JSONファイルからスプレッドシートIDを取得
    if not os.path.exists(spreadsheet_file_path):
        print(f"エラー: スプレッドシートID指定ファイルが見つかりません: {spreadsheet_file_path}")
        sys.exit(1)
    with open(spreadsheet_file_path, 'r', encoding='utf-8') as f:
        file_list = json.load(f)
else:
    print("エラー: config.json に 'drive_folder_id' または 'spreadsheet_file_path' を設定してください。")
    sys.exit(1)

if not file_list:
    print("エラー: ダウンロード対象のスプレッドシートが0件です。")
    sys.exit(1)

# Sheets API サービス（タイトル取得用）
sheets_service = build('sheets', 'v4', credentials=credentials)

has_error = False

# 各スプレッドシートをループで処理
for file in file_list:
    spreadsheet_id = file.get('fileId')
    file_name = file.get('fileName')

    try:
        # ファイル名が未設定の場合は Sheets API から取得
        if not file_name:
            spreadsheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            file_name = spreadsheet_metadata.get('properties', {}).get('title', 'spreadsheet')

        # ファイル名として使えない文字を除去
        safe_title = re.sub(r'[\\/*?:"<>|]', '_', file_name)
        output_filename = f"{safe_title}.pdf"

        # PDFエクスポートURL
        export_url = (
            f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export'
            f'?format=pdf&portrait=true&size=A4&sheetnames=false&printtitle=false'
            f'&pagenumbers=false&gridlines=false&fzr=false'
        )

        # PDFを取得してローカルに保存
        response = authed_session.get(export_url)
        content_type = response.headers.get("Content-Type", "")

        if "application/pdf" in content_type:
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            print(f"保存成功: {output_filename}")
        else:
            print(f"保存失敗: {output_filename} (Content-Type: {content_type})")
            print(f"レスポンス冒頭: {response.text[:300]}")
            has_error = True

    except Exception as e:
        print(f"処理失敗: {file_name or spreadsheet_id}")
        print("エラー内容:", str(e))
        has_error = True

if has_error:
    print("エラー: 1件以上のPDFダウンロードに失敗しました。")
    sys.exit(1)

print(f"完了: 全 {len(file_list)} 件のPDFを正常にダウンロードしました。")
