# CSVデータをテーブルにIMPORTする前のチェックツール

SQLテーブルのDDL定義ファイル(.sql)を元に、CSVファイルのデータがテーブルスキーマ（カラム名とデータ型）を満たしているかを検証するCLIツールです。

## 機能

- DDLファイル(.sql)からテーブルスキーマを解析
- CSVファイルの各レコード・各列をスキーマに対して検証
- データ型の不一致を検出（INT, VARCHAR, DECIMAL, DATE, DATETIME等）
- エラーレポート（行番号と問題のあるカラム名）をCSVファイルに出力

## セットアップ

```bash
# 依存関係のインストール
pip install -r requirements.txt
```

## 使い方

基本的な使い方:
```bash
python main.py --ddl テーブル定義.sql --csv データ.csv
```

オプション付き:
```bash
# エラーレポートの出力先を指定
python main.py --ddl users.sql --csv users.csv --output errors.csv

# CSVファイルのエンコーディングを指定（Shift_JIS等）
python main.py --ddl users.sql --csv users.csv --encoding shift_jis
```

ヘルプの表示:
```bash
python main.py --help
```

## テスト

サンプルファイルを使った動作確認:

```bash
# 正常なCSVファイルのテスト
python main.py --ddl tests/sample_users.sql --csv tests/sample_users_valid.csv

# エラーのあるCSVファイルのテスト
python main.py --ddl tests/sample_users.sql --csv tests/sample_users_invalid.csv
```

## サポートしているデータ型

- **整数型**: INT, BIGINT, SMALLINT, TINYINT（UNSIGNED対応）
- **小数型**: DECIMAL, NUMERIC, FLOAT, DOUBLE
- **文字列型**: VARCHAR, CHAR, TEXT
- **日付・時刻型**: DATE, DATETIME, TIMESTAMP, TIME
- **ブール型**: BOOLEAN, BOOL

## プロジェクト構成

```
precheck/
├── src/
│   ├── ddl_parser.py      # DDLファイルのパース処理
│   ├── validator.py        # データ型バリデーション処理
│   └── csv_checker.py      # CSVファイル検証メインロジック
├── tests/                  # テストデータとサンプル
│   ├── sample_users.sql
│   ├── sample_users_valid.csv
│   └── sample_users_invalid.csv
├── requirements.txt
├── main.py                # エントリーポイント
└── README.md
```

## エラーレポート形式

エラーレポートはCSV形式で以下の列を含みます:
- 行番号: エラーが発生したCSVファイルの行番号
- カラム名: 問題のあるカラム名
- 値: 実際のデータ値
- エラー内容: エラーの詳細説明# prechecker
