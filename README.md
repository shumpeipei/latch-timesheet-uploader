# LATCH 勤務表アップローダー

## 概要

このプロジェクトは、Googleスプレッドシートで作成された勤務表をPDF形式でダウンロードし、勤怠管理システム「LATCH」に自動でアップロードするためのツールです。

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
    -   `google-auth-httplib2`
    -   `google-auth-oauthlib`
    -   `playwright`

## セットアップ

1.  **リポジトリのクローン**
    ```bash
    git clone <repository_url>
    cd latch_timesheet_uploader
    ```

2.  **Pythonライブラリのインストール**
    ```bash
    pip install requests google-api-python-client google-auth-httplib2 google-auth-oauthlib playwright
    ```

3.  **Playwrightのブラウザドライバをインストール**
    ```bash
    playwright install
    ```

4.  **Googleサービスアカウントキーの配置**
    -   Google Cloud Platformでサービスアカウントを作成し、キー（JSONファイル）をダウンロードします。
    -   ダウンロードしたキーファイルの名前を `gen-lang-client-*.json` に変更し、プロジェクトのルートディレクトリに配置します。
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
        "upload_file_path": "アップロードするPDFのファイルパス (例: ./YYYY年MM月_勤務表.pdf)",
        "spreadsheet_file_path": "スプレッドシートIDが記載されたJSONファイルへのパス (例: ./sheets.json)"
    }
    ```
    -   `upload_file_path` の `YYYY` と `MM` は、スクリプト実行時に現在の西暦と月に自動的に置き換えられます。

7.  **スプレッドシートIDファイルの作成**
    -   `config.json` の `spreadsheet_file_path` で指定したパスに、ダウンロード対象のスプレッドシートIDを記載したJSONファイルを作成します。
    -   ファイルの中身は以下の形式で記述します。

    **例 (`sheets.json`):**
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
