"""DDLファイルをパースしてテーブルスキーマ情報を抽出"""
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ColumnDefinition:
    """カラム定義"""
    name: str
    data_type: str
    nullable: bool = True

    def __repr__(self):
        null_str = "NULL" if self.nullable else "NOT NULL"
        return f"{self.name} {self.data_type} {null_str}"


class DDLParser:
    """DDLファイルからテーブルスキーマをパースするクラス"""

    def __init__(self, ddl_file_path: str):
        self.ddl_file_path = ddl_file_path
        self.columns: List[ColumnDefinition] = []

    def parse(self) -> List[ColumnDefinition]:
        """DDLファイルを解析してカラム定義のリストを返す"""
        with open(self.ddl_file_path, 'r', encoding='utf-8') as f:
            ddl_content = f.read()

        self.columns = self._extract_columns(ddl_content)
        return self.columns

    def _extract_columns(self, ddl_content: str) -> List[ColumnDefinition]:
        """CREATE TABLE文からカラム定義を抽出"""
        # CREATE TABLE文を探す
        create_table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\w`.]+\s*\((.*?)\);'
        match = re.search(create_table_pattern, ddl_content, re.IGNORECASE | re.DOTALL)

        if not match:
            raise ValueError("CREATE TABLE文が見つかりません")

        columns_section = match.group(1)
        columns = []

        # カラム定義を1行ずつ処理
        for line in columns_section.split('\n'):
            line = line.strip()
            if not line or line.startswith('PRIMARY KEY') or line.startswith('FOREIGN KEY') or line.startswith('CONSTRAINT') or line.startswith('KEY') or line.startswith('INDEX'):
                continue

            # コメントを除去
            line = re.sub(r'--.*$', '', line)
            line = line.rstrip(',').strip()

            if not line:
                continue

            column = self._parse_column_definition(line)
            if column:
                columns.append(column)

        return columns

    def _parse_column_definition(self, line: str) -> ColumnDefinition:
        """1つのカラム定義をパース"""
        # カラム名を抽出（バッククォートやダブルクォートで囲まれている可能性あり）
        column_name_match = re.match(r'([`"]?\w+[`"]?)\s+(.*)', line)
        if not column_name_match:
            return None

        column_name = column_name_match.group(1).strip('`"')
        rest = column_name_match.group(2)

        # データ型を抽出
        data_type = self._extract_data_type(rest)

        # NULL制約をチェック
        nullable = 'NOT NULL' not in rest.upper()

        return ColumnDefinition(name=column_name, data_type=data_type, nullable=nullable)

    def _extract_data_type(self, definition: str) -> str:
        """カラム定義からデータ型を抽出"""
        # 一般的なデータ型パターン（長いパターンを先にチェック）
        type_patterns = [
            r'(INT(?:EGER)?(?:\(\d+\))?(?:\s+UNSIGNED)?)',
            r'(BIGINT(?:\(\d+\))?(?:\s+UNSIGNED)?)',
            r'(SMALLINT(?:\(\d+\))?(?:\s+UNSIGNED)?)',
            r'(TINYINT(?:\(\d+\))?(?:\s+UNSIGNED)?)',
            r'(DECIMAL(?:\(\d+,\s*\d+\))?)',
            r'(NUMERIC(?:\(\d+,\s*\d+\))?)',
            r'(FLOAT(?:\(\d+,\s*\d+\))?)',
            r'(DOUBLE(?:\s+PRECISION)?(?:\(\d+,\s*\d+\))?)',
            r'(VARCHAR\(\d+\))',
            r'(CHAR\(\d+\))',
            r'(TEXT)',
            r'(DATETIME)',
            r'(TIMESTAMP)',
            r'(DATE)',
            r'(TIME)',
            r'(BOOLEAN)',
            r'(BOOL)',
            r'(BLOB)',
        ]

        for pattern in type_patterns:
            match = re.search(pattern, definition, re.IGNORECASE)
            if match:
                return match.group(1).upper()

        # マッチしない場合は最初の単語を返す
        first_word = definition.split()[0] if definition.split() else 'UNKNOWN'
        return first_word.upper()

    def get_column_names(self) -> List[str]:
        """カラム名のリストを返す"""
        return [col.name for col in self.columns]

    def get_column_map(self) -> Dict[str, ColumnDefinition]:
        """カラム名をキーとした辞書を返す"""
        return {col.name: col for col in self.columns}
