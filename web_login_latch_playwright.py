import json
from datetime import datetime

# 設定ファイルからログイン情報とファイルパスを読み込む
with open("./config.json", encoding="utf-8") as f:
    config = json.load(f)
    login_id = config["login_id"]
    password = config["password"]
    upload_file_paths = config["upload_file_path"]

# ファイルパスの年月を動的に生成
now = datetime.now()
processed_upload_file_paths = [path.replace("YYYY", now.strftime("%Y")).replace("MM", now.strftime("%m")) for path in upload_file_paths]

from playwright.sync_api import sync_playwright, expect
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Trueで非表示、Falseでブラウザ表示
    context = browser.new_context()
    page = context.new_page()
    # ログインページへアクセス
    page.goto("https://latch-tools.com/login")

    # ログイン情報入力
    page.get_by_role("textbox", name="Login ID").fill(login_id)
    page.get_by_role("textbox", name="Password").fill(password)
    page.get_by_role("button", name="Login").click()
    # アサーション：ログイン後のユーザー名表示
    expect(page.locator("text=ようこそ")).to_be_visible()
    page.get_by_role("link", name="crew crew").click()
    # アサーション：画面遷移確認
    expect(page.locator("text=ようこそ")).to_be_visible()
    # 勤怠入力画面に遷移
    page.get_by_role("link", name=" 勤務表").click()
    page.get_by_role("link", name="追加").click()
    
    # 「ファイルを選択 参照」ボタンが2つ表示されるまで待機
    # リストの0番目と1番目のファイルをそれぞれ設定
    page.locator('input[type="file"]').nth(0).set_input_files(processed_upload_file_paths[0])
    page.locator('input[type="file"]').nth(1).set_input_files(processed_upload_file_paths[1])
    page.get_by_role("button", name="保存する").click()

    # 完了確認（ミリ秒）
    page.wait_for_timeout(5000)

    browser.close()