# CSVインポート事前チェックツール - 処理の流れ

## 概要
このツールは、DDLファイル（CREATE TABLE定義）とCSVファイルを比較し、CSVデータがテーブル定義に適合するかを検証します。

## 全体の処理フロー

```mermaid
flowchart TD
    Start([開始]) --> ParseArgs[コマンドライン引数解析]
    ParseArgs --> CheckFiles{DDL/CSVファイル<br/>存在確認}
    CheckFiles -->|ファイル不在| Error1[エラー出力<br/>終了コード: 1]
    CheckFiles -->|存在| InitChecker[CSVCheckerインスタンス生成]

    InitChecker --> Validate[validate メソッド実行]

    Validate --> ParseDDL[DDLParser:<br/>DDLファイル解析]
    ParseDDL --> ExtractColumns[CREATE TABLE文から<br/>カラム定義抽出]
    ExtractColumns --> ColumnMap[カラムマップ作成]

    ColumnMap --> ValidateCSV[CSVファイル検証開始]
    ValidateCSV --> ReadCSV[CSVファイル読み込み<br/>DictReaderで処理]
    ReadCSV --> ValidateHeaders[ヘッダー検証]
    ValidateHeaders --> CheckHeaderMatch{ヘッダーと<br/>DDLカラムの<br/>整合性}

    CheckHeaderMatch -->|不足/余分なカラム| Warning[警告メッセージ出力]
    CheckHeaderMatch -->|一致| RowLoop[各行のループ処理]
    Warning --> RowLoop

    RowLoop --> ValidateRow[行データ検証]
    ValidateRow --> ColumnLoop[各カラムのループ]

    ColumnLoop --> CheckColExists{カラムが<br/>CSV内に存在?}
    CheckColExists -->|不在 & NOT NULL| AddError1[エラー追加:<br/>カラム不在]
    CheckColExists -->|存在| ValidateType[DataTypeValidator:<br/>データ型検証]

    ValidateType --> CheckValue{値が<br/>空文字?}
    CheckValue -->|空 & NOT NULL| AddError2[エラー追加:<br/>NOT NULL制約違反]
    CheckValue -->|空 & NULL許可| NextColumn
    CheckValue -->|値あり| TypeValidation{データ型別検証}

    TypeValidation -->|整数型| ValidateInt[整数検証<br/>UNSIGNED/範囲チェック]
    TypeValidation -->|小数型| ValidateDec[DECIMAL/NUMERIC検証<br/>精度/スケールチェック]
    TypeValidation -->|浮動小数点| ValidateFloat[FLOAT/DOUBLE検証]
    TypeValidation -->|文字列型| ValidateStr[VARCHAR/CHAR検証<br/>長さチェック]
    TypeValidation -->|日付型| ValidateDate[DATE検証<br/>フォーマットチェック]
    TypeValidation -->|日時型| ValidateDateTime[DATETIME/TIMESTAMP検証]
    TypeValidation -->|時刻型| ValidateTime[TIME検証]
    TypeValidation -->|ブール型| ValidateBool[BOOLEAN検証]

    ValidateInt --> CheckValid{検証結果}
    ValidateDec --> CheckValid
    ValidateFloat --> CheckValid
    ValidateStr --> CheckValid
    ValidateDate --> CheckValid
    ValidateDateTime --> CheckValid
    ValidateTime --> CheckValid
    ValidateBool --> CheckValid

    CheckValid -->|NG| AddError3[エラー追加:<br/>型制約違反]
    CheckValid -->|OK| NextColumn[次のカラムへ]
    AddError1 --> NextColumn
    AddError2 --> NextColumn
    AddError3 --> NextColumn

    NextColumn --> MoreColumns{他のカラムが<br/>存在?}
    MoreColumns -->|Yes| ColumnLoop
    MoreColumns -->|No| NextRow[次の行へ]

    NextRow --> MoreRows{他の行が<br/>存在?}
    MoreRows -->|Yes| RowLoop
    MoreRows -->|No| CheckErrors{エラーが<br/>存在?}

    CheckErrors -->|エラーなし| Success[検証成功メッセージ出力<br/>終了コード: 0]
    CheckErrors -->|エラーあり| DisplayErrors[エラーサマリー表示<br/>最大10件]
    DisplayErrors --> ExportErrors[エラーレポート<br/>CSVファイル出力]
    ExportErrors --> Failure[検証失敗<br/>終了コード: 1]

    Error1 --> End([終了])
    Success --> End
    Failure --> End
```

## モジュール構成と役割

### 1. main.py
**役割**: エントリーポイント・CLI制御
- コマンドライン引数の解析
- ファイル存在確認
- CSVCheckerの実行制御
- 結果の表示と終了コード制御

### 2. csv_checker.py
**役割**: 検証のメインロジック
- DDLParserとDataTypeValidatorの統合
- CSVファイルの読み込みと行ごとの処理
- ヘッダー検証
- エラー情報の収集と出力

**主要クラス**:
- `ValidationError`: エラー情報を保持するデータクラス
- `CSVChecker`: 検証処理のメインクラス

### 3. ddl_parser.py
**役割**: DDL解析
- DDLファイルからCREATE TABLE文を抽出
- カラム定義（名前、データ型、NULL制約）のパース
- カラム情報を構造化データとして提供

**主要クラス**:
- `ColumnDefinition`: カラム定義を保持するデータクラス
- `DDLParser`: DDL解析クラス

### 4. validator.py
**役割**: データ型別のバリデーション
- 各データ型に応じた検証ロジック
- 型固有の制約チェック（範囲、精度、フォーマット等）

**対応データ型**:
- 整数型: INT, BIGINT, SMALLINT, TINYINT（UNSIGNED対応）
- 小数型: DECIMAL, NUMERIC（精度/スケール検証）
- 浮動小数点型: FLOAT, DOUBLE
- 文字列型: VARCHAR, CHAR（長さ検証）
- 日付時刻型: DATE, DATETIME, TIMESTAMP, TIME
- ブール型: BOOLEAN, BOOL
- テキスト型: TEXT

## 詳細な処理シーケンス

```mermaid
sequenceDiagram
    participant User
    participant Main
    participant CSVChecker
    participant DDLParser
    participant Validator
    participant FileSystem

    User->>Main: 実行 (DDL, CSV指定)
    Main->>FileSystem: ファイル存在確認
    FileSystem-->>Main: 確認結果

    Main->>CSVChecker: インスタンス生成
    Main->>CSVChecker: validate()

    CSVChecker->>DDLParser: インスタンス生成
    CSVChecker->>DDLParser: parse()
    DDLParser->>FileSystem: DDLファイル読み込み
    FileSystem-->>DDLParser: DDL内容
    DDLParser->>DDLParser: CREATE TABLE抽出
    DDLParser->>DDLParser: カラム定義パース
    DDLParser-->>CSVChecker: カラム定義リスト

    CSVChecker->>DDLParser: get_column_map()
    DDLParser-->>CSVChecker: カラムマップ

    CSVChecker->>FileSystem: CSVファイル読み込み
    FileSystem-->>CSVChecker: CSV内容

    CSVChecker->>CSVChecker: ヘッダー検証

    loop 各行
        loop 各カラム
            CSVChecker->>Validator: validate(値, データ型, NULL許可)

            alt 空値チェック
                Validator->>Validator: NULL制約検証
            else データ型検証
                alt 整数型
                    Validator->>Validator: 整数検証
                else 小数型
                    Validator->>Validator: DECIMAL検証
                else 文字列型
                    Validator->>Validator: 長さ検証
                else 日付時刻型
                    Validator->>Validator: フォーマット検証
                else その他
                    Validator->>Validator: 型別検証
                end
            end

            Validator-->>CSVChecker: (検証結果, エラーメッセージ)

            alt 検証失敗
                CSVChecker->>CSVChecker: エラー追加
            end
        end
    end

    CSVChecker-->>Main: (検証結果, エラーリスト)

    alt エラーあり
        Main->>CSVChecker: export_errors_to_file()
        CSVChecker->>FileSystem: エラーレポート出力
    end

    Main->>User: 検証結果表示
    Main->>User: 終了コード返却
```

## エラーハンドリング

### 終了コード
- **0**: 検証成功（全レコードが適合）
- **1**: 検証失敗（エラーあり）、またはファイル不在
- **2**: 実行時例外

### エラーの種類
1. **ファイルレベル**
   - DDL/CSVファイルが存在しない
   - ファイル読み込みエラー
   - CSVヘッダーが存在しない

2. **スキーマレベル**
   - DDLに定義されているがCSVに存在しないカラム（警告）
   - CSVに存在するがDDLに定義されていないカラム（警告）

3. **データレベル**
   - NOT NULL制約違反
   - データ型不一致
   - 範囲外の値（整数型）
   - 精度/スケール超過（DECIMAL/NUMERIC）
   - 文字列長超過（VARCHAR/CHAR）
   - フォーマット不正（日付時刻型）
   - UNSIGNED制約違反

## 出力形式

### コンソール出力
- ツール実行情報（ファイルパス、エンコーディング）
- DDL解析結果（カラム数、カラム定義）
- ヘッダー検証の警告
- 検証結果（成功/失敗）
- エラーサマリー（最大10件表示）

### エラーレポートファイル (CSV)
```csv
行番号,カラム名,値,エラー内容
2,"age","abc","整数ではありません"
3,"email","verylongemail@example.com","文字列長が50を超えています（実際: 55）"
```

## 使用例

```bash
# 基本的な使用法
python3 main.py --ddl users.sql --csv users.csv

# エンコーディング指定
python3 main.py --ddl users.sql --csv users.csv --encoding shift_jis

# 出力ファイル指定
python3 main.py --ddl users.sql --csv users.csv --output errors.csv
```

## 拡張性

このツールは以下の拡張が可能です:
- 新しいデータ型のサポート追加（`validator.py`）
- カスタム制約の追加（UNIQUE, CHECK等）
- 複数テーブルの同時検証
- JSON/XML等の他フォーマット対応
- データベース直接接続機能
