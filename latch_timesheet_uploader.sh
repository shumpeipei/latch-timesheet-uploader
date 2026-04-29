#! /bin/bash
# このシェルスクリプトは、指定されたタスクを自動化するためのものです。
# 使用方法や引数、動作概要については、各関数や処理部分のコメントを参照してください。
# 作成日: 2025-07-15
# 最終更新日: 2025-07-15
# 作成者: shumpei koike
# 必要な環境: bash
#
# 使い方:
#   ./upload_pdf_latch.sh
# オプション:
#   なし
#
# 注意事項:
#   実行前に必要な権限や環境設定を確認してください。

# スプレッドシートからPDFを取得し、指定されたフォルダに保存する関数
python download_pdf.py
download_status=$?
if [ $download_status -ne 0 ]; then
    echo "PDFのダウンロードに失敗しました。処理を中断します。終了コード: $download_status"
    exit $download_status
fi

# latchのウェブサイトにログインし、PDFをアップロードする関数
python web_login_latch_playwright.py
upload_status=$?
if [ $upload_status -ne 0 ]; then
    echo "LATCHへのPDFアップロードに失敗しました。処理を中断します。終了コード: $upload_status"
    exit $upload_status
fi

# DLしたPDFを削除
rm -f *.pdf
# 削除できた場合にはメッセージを表示
if [ $? -eq 0 ]; then
    echo "PDFファイルの削除に成功しました。"
else
    echo "PDFファイルの削除に失敗しました。"
    exit 1
fi
