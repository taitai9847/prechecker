import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ColumnDefinition:
    name: str
    data_type: str
    nullable: bool = True
    auto_increment: bool = False

    def __repr__(self):
        null_str = "NULL" if self.nullable else "NOT NULL"
        auto_str = " AUTO_INCREMENT" if self.auto_increment else ""
        return f"{self.name} {self.data_type} {null_str}{auto_str}"


class DDLParser:

    def __init__(self, ddl_file_path: str):
        self.ddl_file_path = ddl_file_path
        self.columns: List[ColumnDefinition] = []

    def parse(self) -> List[ColumnDefinition]:
        with open(self.ddl_file_path, 'r', encoding='utf-8') as f:
            ddl_content = f.read()

        self.columns = self._extract_columns(ddl_content)
        return self.columns

    def _extract_columns(self, ddl_content: str) -> List[ColumnDefinition]:
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

        # AUTO_INCREMENT/SERIAL検出
        auto_increment = self._is_auto_increment(rest, data_type)

        return ColumnDefinition(
            name=column_name,
            data_type=data_type,
            nullable=nullable,
            auto_increment=auto_increment
        )

    def _is_auto_increment(self, definition: str, data_type: str) -> bool:
        """
        AUTO_INCREMENT/SERIAL属性を検出

        対応パターン:
        - MySQL: AUTO_INCREMENT
        - PostgreSQL: SERIAL, BIGSERIAL, SMALLSERIAL
        - PostgreSQL: GENERATED ... AS IDENTITY
        - SQL Server: IDENTITY
        """
        definition_upper = definition.upper()

        # AUTO_INCREMENTキーワード
        if 'AUTO_INCREMENT' in definition_upper:
            return True

        # PostgreSQL SERIAL型
        if data_type.upper() in ('SERIAL', 'BIGSERIAL', 'SMALLSERIAL'):
            return True

        # GENERATED ... AS IDENTITY
        if 'GENERATED' in definition_upper and 'IDENTITY' in definition_upper:
            return True

        # SQL Server IDENTITY
        if re.search(r'IDENTITY\s*\(', definition_upper):
            return True

        return False

    def _extract_data_type(self, definition: str) -> str:
        type_patterns = [
            # PostgreSQL SERIAL型を追加
            r'(BIGSERIAL)',
            r'(SERIAL)',
            r'(SMALLSERIAL)',
            # 既存の型
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
        return [col.name for col in self.columns]

    def get_column_map(self) -> Dict[str, ColumnDefinition]:
        return {col.name: col for col in self.columns}
