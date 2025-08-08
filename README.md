# LATCH 勤務表アップローダー

## 概要

このプロジェクトは、Google スプレッドシートで作成された勤務表を PDF 形式でダウンロードし、勤怠管理システム「LATCH」に自動でアップロードするためのツールです。シェルスクリプト `latch_timesheet_uploader.sh` が PDF のダウンロード、LATCH へのアップロード、処理後の PDF の削除までを一括で行います。

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

-   Python 3
-   Bash
-   Google Cloud Platformのサービスアカウント
-   以下のPythonライブラリ:
    -   `requests`
    -   `google-api-python-client`
    -   `google-auth`
    -   `playwright`

## セットアップ（自動化フロー1 勤務表の自動作成）
1. 勤務表テンプレートのスプレッドシートのApps scriptに「copySpreadsheetFromTemplate.js」のソースを貼り付けて月次実行するようにスケジューリングする。

## セットアップ（自動化フロー3,4 PDFダウンロード、latchアップロード）

1.  **リポジトリのクローン**
    ```bash
    git clone <repository_url>
    cd latch_timesheet_uploader
    ```

2.  **Pythonライブラリのインストール**
    ```bash
    pip install requests google-api-python-client google-auth playwright
    ```

3.  **Playwrightのブラウザドライバをインストール**
    ```bash
    playwright install
    ```

4.  **Googleサービスアカウントキーの配置**
    -   Google Cloud Platformでサービスアカウントを作成し、キー（JSONファイル）をダウンロードします。
    -   ダウンロードしたキーファイルをブランチディレクトリ直下に格納してください。
    -   **重要**: このキーファイルには機密情報が含まれるため、Gitで管理しないでください。`.gitignore` にデフォルトで設定されています。

5.  **Googleスプレッドシートの共有設定**
    -   ダウンロードしたいGoogleスプレッドシートを開き、共有設定でサービスアカウントのメールアドレス（キーファイル内に記載されています）に「閲覧者」以上の権限を与えます。

6.  **設定ファイルの作成**
    -   `config_template.json` をコピーして `config.json` という名前のファイルを作成します。
    -   `config.json` を開き、各項目を自分の情報に合わせて編集します。

    **`config.json` の内容:**
    ```json
    {
        "login_id": "LATCHのログインID",
        "password": "LATCHのパスワード",
        "upload_file_path": [
            "アップロードするPDFのファイルパス1 (例: ./YYYY年MM月_勤務表_現場.pdf)",
            "アップロードするPDFのファイルパス2 (例: ./YYYY年MM月_勤務表_自社.pdf)"
        ],
        "spreadsheet_file_path": "スプレッドシートIDが記載されたJSONファイルへのパス (例: ./spreadsheet_ids.json)",
        "service_account_file_path": "4で取得した Google サービスアカウントキーのファイルパス（例：./gen-lang-client-123456.json)"
    }
    ```
    -   `upload_file_path` の `YYYY` と `MM` は、スクリプト実行時に現在の西暦と月に自動的に置き換えられます。

7.  **スプレッドシートIDファイルの作成**
    -   `config.json` の `spreadsheet_file_path` で指定したパスに、ダウンロード対象のスプレッドシート ID を記載した JSON ファイルを作成します。`copySpreadsheetFromTemplate.js` を実行した場合は同じフォルダに `spreadsheet_ids.json` として出力されます。
    -   ファイルの中身は以下の形式で記述します。

    **例 (`spreadsheet_ids.json`):**
    ```json
    [
        {
            "fileId": "ここに1つ目のスプレッドシートID"
        },
        {
            "fileId": "ここに2つ目のスプレッドシートID"
        }
    ]
    ```

## 使用方法

すべての設定が完了したら、以下のコマンドを実行します。

```bash
./latch_timesheet_uploader.sh
```

スクリプトが実行され、PDFのダウンロードとLATCHへのアップロードが自動的に行われます。
