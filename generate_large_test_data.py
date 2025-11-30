#!/usr/bin/env python3
"""300カラムのDDLと50000行のテストデータを生成するスクリプト"""
import random
from datetime import datetime, timedelta

def generate_ddl():
    """300カラムのDDL定義を生成"""
    ddl = """-- ユーザーテーブルのサンプルDDL（300カラム）
CREATE TABLE users (
    id INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    age INT,
    balance DECIMAL(10,2),
    is_active BOOLEAN NOT NULL,
    created_at DATETIME,
    birth_date DATE,
"""

    # VARCHAR型ダミーカラム（50個）
    for i in range(1, 51):
        ddl += f"    dummy_varchar_{i:03d} VARCHAR(100),\n"

    # INT型ダミーカラム（50個）
    for i in range(1, 51):
        ddl += f"    dummy_int_{i:03d} INT,\n"

    # DECIMAL型ダミーカラム（50個）
    for i in range(1, 51):
        ddl += f"    dummy_decimal_{i:03d} DECIMAL(10,2),\n"

    # DATE型ダミーカラム（50個）
    for i in range(1, 51):
        ddl += f"    dummy_date_{i:03d} DATE,\n"

    # DATETIME型ダミーカラム（50個）
    for i in range(1, 51):
        ddl += f"    dummy_datetime_{i:03d} DATETIME,\n"

    # BOOLEAN型ダミーカラム（42個）
    for i in range(1, 42):
        ddl += f"    dummy_boolean_{i:03d} BOOLEAN,\n"

    # 最後のカラム（カンマなし）
    ddl += f"    dummy_boolean_042 BOOLEAN\n"
    ddl += ");\n"

    return ddl

def generate_csv_data(num_rows=50000):
    """50000行のテストデータを生成（validとinvalidデータを含む）"""

    # ヘッダー生成
    headers = ["id", "username", "email", "age", "balance", "is_active", "created_at", "birth_date"]

    # ダミーカラムのヘッダー追加
    for i in range(1, 51):
        headers.append(f"dummy_varchar_{i:03d}")
    for i in range(1, 51):
        headers.append(f"dummy_int_{i:03d}")
    for i in range(1, 51):
        headers.append(f"dummy_decimal_{i:03d}")
    for i in range(1, 51):
        headers.append(f"dummy_date_{i:03d}")
    for i in range(1, 51):
        headers.append(f"dummy_datetime_{i:03d}")
    for i in range(1, 43):
        headers.append(f"dummy_boolean_{i:03d}")

    # CSVヘッダー
    csv_content = ",".join(headers) + "\n"

    # データ行生成
    base_date = datetime(2020, 1, 1)
    bool_values = ['true', 'false', '1', '0', 'yes', 'no']
    invalid_bool_values = ['maybe', 'invalid', 'unknown', 'abc']
    invalid_int_values = ['abc', 'text', 'invalid', 'NaN']
    invalid_decimal_values = ['not_a_number', 'invalid', 'abc123']

    for row_id in range(1, num_rows + 1):
        row_data = []

        # 1%の確率でinvalidなデータを生成
        is_invalid_row = random.random() < 0.01

        # 基本カラム
        row_data.append(str(row_id))

        # username (NOT NULL)
        if is_invalid_row and random.random() < 0.1:
            row_data.append("NULL" if random.random() < 0.5 else "")
        elif is_invalid_row and random.random() < 0.1:
            # VARCHAR(50)制約違反（長すぎる文字列）
            row_data.append("this_is_a_very_long_username_that_exceeds_varchar_50_limit_for_sure")
        else:
            row_data.append(f"user{row_id}")

        # email (NOT NULL)
        if is_invalid_row and random.random() < 0.1:
            row_data.append("NULL" if random.random() < 0.5 else "")
        elif is_invalid_row and random.random() < 0.1:
            # VARCHAR(100)制約違反
            row_data.append("this_is_an_extremely_long_email_address_that_definitely_exceeds_the_varchar_100_limit_set_in_ddl@example.com")
        else:
            row_data.append(f"user{row_id}@example.com")

        # age (INT, nullable)
        if is_invalid_row and random.random() < 0.2:
            row_data.append(random.choice(invalid_int_values))
        elif is_invalid_row and random.random() < 0.1:
            row_data.append(str(random.randint(2147483648, 3000000000)))  # INT範囲外
        else:
            row_data.append(str(random.randint(18, 80)) if random.random() > 0.1 else "")

        # balance (DECIMAL(10,2), nullable)
        if is_invalid_row and random.random() < 0.2:
            row_data.append(random.choice(invalid_decimal_values))
        elif is_invalid_row and random.random() < 0.1:
            row_data.append("99999999999.99")  # 全体桁数超過
        elif is_invalid_row and random.random() < 0.1:
            row_data.append(f"{random.uniform(0, 10000):.4f}")  # 小数部桁数超過
        else:
            row_data.append(f"{random.uniform(0, 100000):.2f}" if random.random() > 0.1 else "")

        # is_active (BOOLEAN, NOT NULL)
        if is_invalid_row and random.random() < 0.2:
            row_data.append(random.choice(invalid_bool_values))
        elif is_invalid_row and random.random() < 0.1:
            row_data.append("NULL")
        else:
            row_data.append(random.choice(bool_values))

        # created_at (DATETIME, nullable)
        if is_invalid_row and random.random() < 0.2:
            row_data.append(random.choice(['invalid_datetime', 'not_a_date', '2024-13-01 10:00:00']))
        elif random.random() > 0.1:
            dt = base_date + timedelta(days=random.randint(0, 1825))
            row_data.append(dt.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            row_data.append("")

        # birth_date (DATE, nullable)
        if is_invalid_row and random.random() < 0.2:
            row_data.append(random.choice(['invalid_date', '2024-13-40', '1990-02-30', 'not_a_date']))
        elif random.random() > 0.1:
            bd = datetime(random.randint(1940, 2010), random.randint(1, 12), random.randint(1, 28))
            row_data.append(bd.strftime("%Y-%m-%d"))
        else:
            row_data.append("")

        # VARCHAR型ダミーカラム（50個）
        for i in range(50):
            if is_invalid_row and i < 5 and random.random() < 0.3:
                # VARCHAR(100)制約違反
                row_data.append("a" * 150)
            elif random.random() > 0.2:
                row_data.append(f"text_{random.randint(1, 1000)}")
            else:
                row_data.append("")

        # INT型ダミーカラム（50個）
        for i in range(50):
            if is_invalid_row and i < 5 and random.random() < 0.3:
                row_data.append(random.choice(invalid_int_values))
            elif random.random() > 0.2:
                row_data.append(str(random.randint(1, 10000)))
            else:
                row_data.append("")

        # DECIMAL型ダミーカラム（50個）
        for i in range(50):
            if is_invalid_row and i < 5 and random.random() < 0.3:
                row_data.append(random.choice(invalid_decimal_values))
            elif random.random() > 0.2:
                row_data.append(f"{random.uniform(0, 10000):.2f}")
            else:
                row_data.append("")

        # DATE型ダミーカラム（50個）
        for i in range(50):
            if is_invalid_row and i < 5 and random.random() < 0.3:
                row_data.append(random.choice(['invalid', '2024-99-99', 'not_date']))
            elif random.random() > 0.2:
                d = datetime(random.randint(2000, 2024), random.randint(1, 12), random.randint(1, 28))
                row_data.append(d.strftime("%Y-%m-%d"))
            else:
                row_data.append("")

        # DATETIME型ダミーカラム（50個）
        for i in range(50):
            if is_invalid_row and i < 5 and random.random() < 0.3:
                row_data.append(random.choice(['invalid', '2024-01-01 99:99:99', 'not_datetime']))
            elif random.random() > 0.2:
                dt = base_date + timedelta(days=random.randint(0, 1825), hours=random.randint(0, 23))
                row_data.append(dt.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                row_data.append("")

        # BOOLEAN型ダミーカラム（42個）
        for i in range(42):
            if is_invalid_row and i < 5 and random.random() < 0.3:
                row_data.append(random.choice(invalid_bool_values))
            elif random.random() > 0.2:
                row_data.append(random.choice(bool_values))
            else:
                row_data.append("")

        csv_content += ",".join(row_data) + "\n"

        # 進捗表示（1000行ごと）
        if row_id % 1000 == 0:
            print(f"生成中: {row_id}/{num_rows} 行")

    return csv_content

def main():
    print("300カラムのDDL定義を生成中...")
    ddl_content = generate_ddl()

    with open("tests/sample_users.sql", "w", encoding="utf-8") as f:
        f.write(ddl_content)
    print("✓ DDLファイルを生成しました: tests/sample_users.sql")

    print("\n50000行のテストデータを生成中...")
    csv_content = generate_csv_data(50000)

    with open("tests/sample_users_valid.csv", "w", encoding="utf-8") as f:
        f.write(csv_content)
    print("✓ CSVファイルを生成しました: tests/sample_users_valid.csv")

    print("\n完了しました！")

if __name__ == "__main__":
    main()
