"""データ型のバリデーション処理"""
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Tuple


class DataTypeValidator:
    """データ型のバリデーションを行うクラス"""

    @staticmethod
    def validate(value: str, data_type: str, nullable: bool) -> Tuple[bool, str]:
        """
        値が指定されたデータ型に適合するかを検証

        Args:
            value: 検証する値
            data_type: データ型（例: VARCHAR(50), INT, DATE）
            nullable: NULL許可フラグ

        Returns:
            (is_valid, error_message) のタプル
        """
        # 空文字列の処理
        if value == '' or value is None:
            if nullable:
                return True, ""
            else:
                return False, "NOT NULL制約違反"

        # データ型に応じたバリデーション
        data_type_upper = data_type.upper()

        # 整数型
        if data_type_upper.startswith('INT') or data_type_upper.startswith('BIGINT') or \
           data_type_upper.startswith('SMALLINT') or data_type_upper.startswith('TINYINT'):
            return DataTypeValidator._validate_integer(value, data_type_upper)

        # 小数型
        if data_type_upper.startswith('DECIMAL') or data_type_upper.startswith('NUMERIC'):
            return DataTypeValidator._validate_decimal(value, data_type_upper)

        # 浮動小数点型
        if data_type_upper.startswith('FLOAT') or data_type_upper.startswith('DOUBLE'):
            return DataTypeValidator._validate_float(value)

        # 文字列型
        if data_type_upper.startswith('VARCHAR') or data_type_upper.startswith('CHAR'):
            return DataTypeValidator._validate_string(value, data_type_upper)

        # テキスト型
        if data_type_upper == 'TEXT':
            return True, ""

        # 日付型
        if data_type_upper == 'DATE':
            return DataTypeValidator._validate_date(value)

        # 日時型
        if data_type_upper == 'DATETIME' or data_type_upper == 'TIMESTAMP':
            return DataTypeValidator._validate_datetime(value)

        # 時刻型
        if data_type_upper == 'TIME':
            return DataTypeValidator._validate_time(value)

        # ブール型
        if data_type_upper in ('BOOLEAN', 'BOOL'):
            return DataTypeValidator._validate_boolean(value)

        # 未対応のデータ型
        return True, f"未対応のデータ型: {data_type}"

    @staticmethod
    def _validate_integer(value: str, data_type: str) -> Tuple[bool, str]:
        """整数型のバリデーション"""
        try:
            num = int(value)

            # UNSIGNED チェック
            if 'UNSIGNED' in data_type and num < 0:
                return False, "UNSIGNED型に負の値は許可されません"

            # 範囲チェック
            if data_type.startswith('TINYINT'):
                min_val, max_val = (-128, 127) if 'UNSIGNED' not in data_type else (0, 255)
            elif data_type.startswith('SMALLINT'):
                min_val, max_val = (-32768, 32767) if 'UNSIGNED' not in data_type else (0, 65535)
            elif data_type.startswith('INT'):
                min_val, max_val = (-2147483648, 2147483647) if 'UNSIGNED' not in data_type else (0, 4294967295)
            elif data_type.startswith('BIGINT'):
                min_val, max_val = (-9223372036854775808, 9223372036854775807) if 'UNSIGNED' not in data_type else (0, 18446744073709551615)
            else:
                return True, ""

            if not (min_val <= num <= max_val):
                return False, f"値が範囲外です（{min_val}〜{max_val}）"

            return True, ""
        except ValueError:
            return False, "整数ではありません"

    @staticmethod
    def _validate_decimal(value: str, data_type: str) -> Tuple[bool, str]:
        """DECIMAL/NUMERIC型のバリデーション"""
        try:
            dec_value = Decimal(value)

            # 精度チェック（例: DECIMAL(10,2)）
            precision_match = re.search(r'\((\d+),\s*(\d+)\)', data_type)
            if precision_match:
                precision = int(precision_match.group(1))
                scale = int(precision_match.group(2))

                # 文字列から整数部と小数部を取得
                value_str = str(dec_value)
                if '.' in value_str:
                    int_part, dec_part = value_str.lstrip('-').split('.')
                else:
                    int_part = value_str.lstrip('-')
                    dec_part = ''

                int_digits = len(int_part)
                dec_digits = len(dec_part)

                if int_digits + dec_digits > precision:
                    return False, f"全体桁数が{precision}を超えています"
                if dec_digits > scale:
                    return False, f"小数部が{scale}桁を超えています"

            return True, ""
        except InvalidOperation:
            return False, "数値ではありません"

    @staticmethod
    def _validate_float(value: str) -> Tuple[bool, str]:
        """浮動小数点型のバリデーション"""
        try:
            float(value)
            return True, ""
        except ValueError:
            return False, "浮動小数点数ではありません"

    @staticmethod
    def _validate_string(value: str, data_type: str) -> Tuple[bool, str]:
        """文字列型のバリデーション"""
        # 長さチェック（例: VARCHAR(50)）
        length_match = re.search(r'\((\d+)\)', data_type)
        if length_match:
            max_length = int(length_match.group(1))
            if len(value) > max_length:
                return False, f"文字列長が{max_length}を超えています（実際: {len(value)}）"

        return True, ""

    @staticmethod
    def _validate_date(value: str) -> Tuple[bool, str]:
        """DATE型のバリデーション"""
        date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d']

        for fmt in date_formats:
            try:
                datetime.strptime(value, fmt)
                return True, ""
            except ValueError:
                continue

        return False, "日付形式が正しくありません（YYYY-MM-DD等）"

    @staticmethod
    def _validate_datetime(value: str) -> Tuple[bool, str]:
        """DATETIME/TIMESTAMP型のバリデーション"""
        datetime_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y/%m/%d %H:%M:%S',
            '%Y%m%d%H%M%S',
        ]

        for fmt in datetime_formats:
            try:
                datetime.strptime(value, fmt)
                return True, ""
            except ValueError:
                continue

        return False, "日時形式が正しくありません（YYYY-MM-DD HH:MM:SS等）"

    @staticmethod
    def _validate_time(value: str) -> Tuple[bool, str]:
        """TIME型のバリデーション"""
        time_formats = ['%H:%M:%S', '%H:%M']

        for fmt in time_formats:
            try:
                datetime.strptime(value, fmt)
                return True, ""
            except ValueError:
                continue

        return False, "時刻形式が正しくありません（HH:MM:SS等）"

    @staticmethod
    def _validate_boolean(value: str) -> Tuple[bool, str]:
        """BOOLEAN型のバリデーション"""
        value_lower = value.lower()
        valid_values = ['true', 'false', '1', '0', 't', 'f', 'yes', 'no', 'y', 'n']

        if value_lower in valid_values:
            return True, ""

        return False, "ブール値ではありません（true/false, 1/0等）"
