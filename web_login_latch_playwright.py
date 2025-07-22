import json
from datetime import datetime

# 設定ファイルからログイン情報とファイルパスを読み込む
with open("./config.json", encoding="utf-8") as f:
    config = json.load(f)
    login_id = config["login_id"]
    password = config["password"]
    upload_file_path = config["upload_file_path"]

# ファイルパスの年月を動的に生成
now = datetime.now()
upload_file_path = upload_file_path.replace("YYYY", now.strftime("%Y")).replace("MM", now.strftime("%m"))

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
    page.locator('input[type="file"]').nth(0).set_input_files(upload_file_path)
    page.locator('input[type="file"]').nth(1).set_input_files(upload_file_path)
    page.get_by_role("button", name="保存する").click()

    # 完了確認（ミリ秒）
    page.wait_for_timeout(5000)

    browser.close()