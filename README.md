# LATCH 勤務表アップローダー

## 概要

このプロジェクトは、Googleスプレッドシートで作成された勤務表をPDF形式でダウンロードし、勤怠管理システム「LATCH」に自動でアップロードするためのツールです。

## 自動化フロー
1. 勤怠テンプレートシートをもとに勤怠シート（現場、自社）を作成
   - copySpreadsheetFromTemplate.jsを参照
2. 勤怠入力
   - 手入力
3. 月末に「2」で作成した勤怠をPDFでローカルにDL
   - download_pdf.pyを参照
4. Latchに「3」でDLしたPDFをアップロード
   - web_login_latch_playwright.pyを参照

## 主な機能
-   Google Drive上の指定されたスプレッドシートをPDFとしてダウンロードします。
-   LATCHに自動でログインします。
-   ダウンロードした勤務表（PDF）をLATCHの勤務表ページにアップロードします。

## 必要なもの

-   [uv](https://docs.astral.sh/uv/)（Pythonパッケージ管理）
-   Bash
-   Google Cloud Platformのサービスアカウント

> 依存ライブラリ（`requests`, `google-api-python-client`, `google-auth-httplib2`, `playwright` 等）は `pyproject.toml` で管理されており、`uv sync` で一括インストールできます。

## セットアップ（自動化フロー1 勤務表の自動作成）
1. 勤務表テンプレートのスプレッドシートのApps scriptに「copySpreadsheetFromTemplate.js」のソースを貼り付けて月次実行するようにスケジューリングする。

## セットアップ（自動化フロー3,4 PDFダウンロード、latchアップロード）
1.  **リポジトリのクローン**
    ```bash
    git clone <repository_url>
    cd latch_timesheet_uploader
    ```

2.  **依存ライブラリのインストール**
    ```bash
    uv sync
    ```
    仮想環境（`.venv`）が自動作成され、`pyproject.toml` に定義されたライブラリがインストールされます。

3.  **Playwrightのブラウザドライバをインストール**
    ```bash
    uv run playwright install chromium
    ```
    ブラウザバイナリは `~/Library/Caches/ms-playwright/` に保存され、全プロジェクトで共有されます。
    シェルスクリプト実行時にも自動で実行されるため、初回以降は手動実行不要です。

4.  **Googleサービスアカウントキーの配置**
    -   Google Cloud Platformでサービスアカウントを作成し、キー（JSONファイル）をダウンロードします。
    -   ダウンロードしたキーファイルをブランチディレクトリ直下に格納してください。
    -   **重要**: このキーファイルには機密情報が含まれるため、Gitで管理しないでください。`.gitignore` にデフォルトで設定されています。

5.  **Google Driveフォルダの共有設定**
    -   勤務表スプレッドシートが格納されているGoogle Driveの親フォルダを開き、共有設定でサービスアカウントのメールアドレス（キーファイル内に記載されている `client_email`）に「閲覧者」以上の権限を与えます。
    -   親フォルダに権限を付与することで、毎月新しく作成されるスプレッドシートにも自動的に閲覧権限が引き継がれます。

6.  **設定ファイルの作成**
    -   `config_template.json` をコピーして `config.json` という名前のファイルを作成します。
    -   `config.json` を開き、各項目を編集します。

    **`config.json` の内容:**
    ```json
    {
        "login_id": "LATCHのログインID",
        "password": "LATCHのパスワード",
        "upload_file_path": [
            "./【BL】名前_現場勤務表_YYYY年MM月分_現場.pdf",
            "./【BL】名前_現場勤務表_YYYY年MM月分_自社.pdf"
        ],
        "drive_folder_id": "Google Drive上の勤務表保存フォルダID",
        "service_account_file_path": "./google-service-account.json"
    }
    ```
    -   `drive_folder_id`: 勤務表が格納されているGoogle DriveフォルダのID（URL `drive.google.com/drive/folders/<FOLDER_ID>` の `<FOLDER_ID>` 部分）を指定します。API経由で当月のスプレッドシートを自動検索するため、毎月IDを更新する必要はありません。
    -   `upload_file_path`: `YYYY` と `MM` は、スクリプト実行時に現在の西暦と月に自動置換されます。ここに指定されたタイトル（`.pdf` を除いた名前）に一致するスプレッドシートをDrive上から自動特定します。
    -   ※ 従来通り `spreadsheet_file_path`（`sheets.json` 形式）を指定してIDを直接指定することも可能です（`drive_folder_id` 未指定時のフォールバック動作）。

## 使用方法

すべての設定が完了したら、以下のコマンドを実行します。

```bash
./latch_timesheet_uploader.sh
```

スクリプトが実行され、PDFのダウンロードとLATCHへのアップロードが自動的に行われます。
