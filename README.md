# 源氏物語学習ツール

源氏物語の原文と現代語訳を使った学習ツールです。

## 機能

### 📖 フラッシュカードモード
- 原文を見て現代語訳を思い出す学習
- ○/△/× で自己評価
- 前後の文脈も表示

### ✏️ 四択クイズモード
- 4つの選択肢から正解を選ぶ
- 似た文章を選択肢として自動生成
- 正解時に演出とconfetti

### 📚 学習モード
- 原文と現代語訳を交互に表示
- ボタンクリックで現代語訳を表示/非表示
- ページネーション対応（10文ずつ表示）

### その他の機能
- 巻の選択
- ランダム/順番通りの出題
- 問題数の選択
- 学習履歴の保存（localStorage）
- 復習モード（間違えた問題のみ）
- 用語注釈のモーダル表示（原文のリンク付き用語をクリック）

## ファイル構成

### リリースファイル
- `index.html` - メインアプリケーション
- `genji_data.js` - 源氏物語データ（21,312文）
- `genji_term_definitions.js` - 用語注釈データ（5,888語）

### メンテナンスツール（Python）
- `genji_scraper.py` - 原文と現代語訳のスクレイピング
- `fetch_term_definitions.py` - 用語注釈のスクレイピング
- `csv_to_json.py` - CSVからJavaScriptファイルへの変換
- `remove_dates_from_csv.py` - データクリーニング

## 使い方

1. ブラウザで `index.html` を開く
2. 学習モードを選択
3. 巻を選択（または全巻）
4. 出題方法と問題数を設定
5. 学習開始

## データソース

http://james.3zoku.com/genji/index.html

## フィードバック・問題報告

バグ報告、機能要望、質問などは [Issues](https://github.com/Nishi-Taiga/Genji_test/issues/new/choose) からお願いします。

- 🐛 [バグ報告](https://github.com/Nishi-Taiga/Genji_test/issues/new?template=bug_report.md)
- ✨ [機能要望](https://github.com/Nishi-Taiga/Genji_test/issues/new?template=feature_request.md)
- ❓ [質問](https://github.com/Nishi-Taiga/Genji_test/issues/new?template=question.md)

## ライセンス

学習目的での使用を前提としています。
