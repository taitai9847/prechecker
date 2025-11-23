"""CSVファイルの検証メインロジック"""
import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass

from .ddl_parser import DDLParser, ColumnDefinition
from .validator import DataTypeValidator


@dataclass
class ValidationError:
    """バリデーションエラー情報"""
    row_number: int
    column_name: str
    value: str
    error_message: str

    def __str__(self):
        return f"行{self.row_number}, カラム'{self.column_name}': {self.error_message} (値: '{self.value}')"


class CSVChecker:
    """CSVファイルの検証を行うクラス"""

    def __init__(self, ddl_file_path: str, csv_file_path: str, encoding: str = 'utf-8'):
        """
        Args:
            ddl_file_path: DDLファイルのパス
            csv_file_path: CSVファイルのパス
            encoding: CSVファイルのエンコーディング（デフォルト: utf-8）
        """
        self.ddl_file_path = ddl_file_path
        self.csv_file_path = csv_file_path
        self.encoding = encoding
        self.errors: List[ValidationError] = []
        self.columns: Dict[str, ColumnDefinition] = {}

    def validate(self) -> Tuple[bool, List[ValidationError]]:
        """
        CSVファイルを検証

        Returns:
            (is_valid, errors) のタプル
            is_valid: 全てのレコードが有効な場合True
            errors: ValidationErrorのリスト
        """
        # DDLをパース
        parser = DDLParser(self.ddl_file_path)
        columns = parser.parse()
        self.columns = parser.get_column_map()

        print(f"DDLファイルを解析しました: {len(self.columns)}カラム")
        for col in columns:
            print(f"  - {col}")

        # CSVファイルを検証
        self.errors = []
        self._validate_csv()

        return len(self.errors) == 0, self.errors

    def _validate_csv(self):
        """CSVファイルを1行ずつ検証"""
        try:
            with open(self.csv_file_path, 'r', encoding=self.encoding, newline='') as csvfile:
                # CSVリーダーを作成（ヘッダー行を読み込む）
                csv_reader = csv.DictReader(csvfile)

                # ヘッダー検証
                csv_headers = csv_reader.fieldnames
                if not csv_headers:
                    raise ValueError("CSVファイルにヘッダーが見つかりません")

                self._validate_headers(csv_headers)

                # データ行を検証
                for row_idx, row in enumerate(csv_reader, start=2):  # ヘッダーの次の行から開始なので2
                    self._validate_row(row_idx, row)

        except FileNotFoundError:
            raise FileNotFoundError(f"CSVファイルが見つかりません: {self.csv_file_path}")
        except Exception as e:
            raise Exception(f"CSVファイルの読み込み中にエラーが発生しました: {e}")

    def _validate_headers(self, csv_headers: List[str]):
        """CSVのヘッダーとDDLのカラム名が一致するか確認"""
        ddl_columns = set(self.columns.keys())
        csv_columns = set(csv_headers)

        # 不足しているカラム
        missing_columns = ddl_columns - csv_columns
        if missing_columns:
            print(f"警告: DDLに定義されているが、CSVに存在しないカラム: {missing_columns}")

        # 余分なカラム
        extra_columns = csv_columns - ddl_columns
        if extra_columns:
            print(f"警告: CSVに存在するが、DDLに定義されていないカラム: {extra_columns}")

    def _validate_row(self, row_number: int, row: Dict[str, str]):
        """1つの行（レコード）を検証"""
        # 全カラムを検証
        for column_name, column_def in self.columns.items():
            # CSVにカラムが存在しない場合
            if column_name not in row:
                if not column_def.nullable:
                    self.errors.append(
                        ValidationError(
                            row_number=row_number,
                            column_name=column_name,
                            value="",
                            error_message="カラムが存在しません（NOT NULL制約違反）"
                        )
                    )
                continue

            value = row[column_name]

            # データ型検証
            is_valid, error_message = DataTypeValidator.validate(
                value, column_def.data_type, column_def.nullable
            )

            if not is_valid:
                self.errors.append(
                    ValidationError(
                        row_number=row_number,
                        column_name=column_name,
                        value=value,
                        error_message=error_message
                    )
                )

    def get_error_summary(self) -> str:
        """エラーサマリーを文字列で返す"""
        if not self.errors:
            return "エラーはありません。"

        summary = f"検出されたエラー: {len(self.errors)}件\n\n"
        for error in self.errors:
            summary += f"{error}\n"

        return summary

    def export_errors_to_file(self, output_file_path: str):
        """エラーをファイルに出力"""
        with open(output_file_path, 'w', encoding='utf-8') as f:
            if not self.errors:
                f.write("エラーはありません。\n")
                return

            # ヘッダー
            f.write("行番号,カラム名,値,エラー内容\n")

            # エラー詳細
            for error in self.errors:
                # CSVとして出力（値にカンマが含まれる可能性を考慮）
                escaped_value = error.value.replace('"', '""')
                escaped_message = error.error_message.replace('"', '""')
                f.write(f'{error.row_number},"{error.column_name}","{escaped_value}","{escaped_message}"\n')

        print(f"エラーレポートを出力しました: {output_file_path}")
