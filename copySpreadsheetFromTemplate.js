/* 以下のソースを勤務表スプレッドシートのApps Scriptに貼り付けて実行してください。
  このスクリプトは、指定したテンプレートから勤務表をコピーし、日付を更新して閲覧権限を付与します。
  また、コピーしたスプレッドシートのIDをJSON形式で保存します。
*/
function copySpreadsheetFromTemplate() {
  const templateId = 'テンプレートにする勤務表のID';
  var fileNameList = ['【BL】{名前}_現場勤務表_YYYY年MM月分_現場', '【BL】{名前}_現場勤務表_YYYY年MM月分_自社'];
  // 参照権限を付与したいメールアドレスを列挙
  const viewerEmails = ['スプレッドシートの参照権限を付与したメールアドレス'];
  // テンプレートファイルの取得、日付修正を行う
  // テンプレートファイルを取得
  var templateFile = DriveApp.getFileById(templateId);

  // コピー元のフォルダを取得（テンプレートが含まれるフォルダ）
  var folders = templateFile.getParents();
  if (!folders.hasNext()) {
    Logger.log("テンプレートのフォルダが見つかりませんでした");
    return;
  }
  var targetFolder = folders.next(); // 最初のフォルダを取得
  // テンプレートのスプレッドシートを開く
  var templateSpreadsheet = SpreadsheetApp.openById(templateId);
  var sheet = templateSpreadsheet.getSheetByName("勤務表"); // シート名を指定
  // 日本のタイムゾーンで現在の日付を取得
  var today = new Date();
  var todayJST = Utilities.formatDate(today, "Asia/Tokyo", "yyyy/MM"); // JSTに補正
  // 勤務表シート存在チェック
  if (sheet) {
    // D3セルに日本時間での日付を入力
    sheet.getRange("D3").setValue(todayJST);
  } else {
    Logger.log("シート「勤務表」が見つかりませんでした");
    return;
  }

  // ファイル情報を保持するリスト
  const resultList = [];

  // ファイルコピー、日付変更処理
  for (var i = 0; i < fileNameList.length; i++) {
    var fileName = replacedString(fileNameList[i]);
    // 同名ファイルがあれば削除（上書き相当）
    deleteIfExists(targetFolder, fileName);

    var newSpreadsheet = templateFile.makeCopy(fileName, targetFolder);
    var newSpreadsheetId = newSpreadsheet.getId();
    // コピー後のスプレッドシートを開いてD3に書き込む
    var newSheet = SpreadsheetApp.openById(newSpreadsheetId).getSheetByName("勤務表");
    if (newSheet) {
      newSheet.getRange("D3").setValue(todayJST);
    }
    // 閲覧権限を追加する
    viewerEmails.forEach(email => {
      newSpreadsheet.addViewer(email); // これで閲覧権限を付与
    });
    Logger.log('New Spreadsheet ID: ' + newSpreadsheetId);
    // リストに追加
    resultList.push({
      fileName: fileName,
      fileId: newSpreadsheetId
    });
  }
  // JSON形式でGoogle Driveにファイル出力
  const json = JSON.stringify(resultList, null, 2); // 整形付き
  const jsonFileName = "spreadsheet_ids.json";
  // 関数を使ってJSON出力
  saveJsonFileWithOverwrite(targetFolder, jsonFileName, json);
}

function replacedString(inputString) {
  var date = new Date();
  var currentYear = date.getFullYear();
  // 月は2桁表示にする（例：01）
  var currentMonth = (date.getMonth() + 1).toString().padStart(2, '0');

  var replacedString = inputString.replace(/YYYY/g, currentYear);
  replacedString = replacedString.replace(/MM/g, currentMonth);

  return replacedString;
}

function deleteIfExists(folder, fileName) {
  const files = folder.getFilesByName(fileName);
  while (files.hasNext()) {
    const file = files.next();
    file.setTrashed(true); // ごみ箱に移動（完全削除は不可）
  }
}

function saveJsonFileWithOverwrite(folder, fileName, jsonContent) {
  // フォルダ内に同名ファイルがあれば削除（ごみ箱移動）
  const files = folder.getFilesByName(fileName);
  while (files.hasNext()) {
    const file = files.next();
    file.setTrashed(true); // ごみ箱に移動（完全削除は不可）
  }

  // 新規作成
  const blob = Utilities.newBlob(jsonContent, "application/json", fileName);
  const file = folder.createFile(blob);
  Logger.log("JSONファイル保存済み: " + file.getUrl());
}
