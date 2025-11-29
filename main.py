"""CSVインポート事前チェックツール - メインエントリーポイント"""
import argparse
import sys
from pathlib import Path

from src.csv_checker import CSVChecker


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='CSVデータをテーブルにIMPORTする前のチェックツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 main.py --ddl users.sql --csv users.csv
  python3 main.py --ddl users.sql --csv users.csv --output errors.csv
  python3 main.py --ddl users.sql --csv users.csv --encoding shift_jis
        """
    )

    parser.add_argument(
        '--ddl',
        required=True,
        help='DDLファイルのパス（例: users.sql）'
    )

    parser.add_argument(
        '--csv',
        required=True,
        help='検証するCSVファイルのパス（例: users.csv）'
    )

    parser.add_argument(
        '--output',
        default='validation_errors.csv',
        help='エラーレポートの出力先ファイルパス（デフォルト: validation_errors.csv）'
    )

    parser.add_argument(
        '--encoding',
        default='utf-8',
        help='CSVファイルのエンコーディング（デフォルト: utf-8）'
    )

    args = parser.parse_args()

    # ファイルの存在確認
    ddl_path = Path(args.ddl)
    csv_path = Path(args.csv)

    if not ddl_path.exists():
        print(f"エラー: DDLファイルが見つかりません: {args.ddl}", file=sys.stderr)
        sys.exit(1)

    if not csv_path.exists():
        print(f"エラー: CSVファイルが見つかりません: {args.csv}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("CSVインポート事前チェックツール")
    print("=" * 60)
    print(f"DDLファイル: {args.ddl}")
    print(f"CSVファイル: {args.csv}")
    print(f"エンコーディング: {args.encoding}")
    print("=" * 60)
    print()

    try:
        # CSVチェッカーを実行
        checker = CSVChecker(args.ddl, args.csv, encoding=args.encoding)
        is_valid, errors = checker.validate()

        print()
        print("=" * 60)

        if is_valid:
            print("検証結果: 成功")
            print("全てのレコードがテーブル定義に適合しています。")
        else:
            print("検証結果: 失敗")
            print(f"検出されたエラー: {len(errors)}件")
            print()

            # エラーサマリーを表示（最大10件）
            print("エラーサマリー（最大10件表示）:")
            for i, error in enumerate(errors[:10], 1):
                print(f"  {i}. {error}")

            if len(errors) > 10:
                print(f"  ... 他{len(errors) - 10}件のエラー")

            # エラーレポートをファイルに出力
            print()
            checker.export_errors_to_file(args.output)

        print("=" * 60)

        # 終了コード
        sys.exit(0 if is_valid else 1)

    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
