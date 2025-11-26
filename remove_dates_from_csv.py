#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSVから日付データを削除するスクリプト
"""

import csv
import re

def remove_dates(text):
    """テキストから日付パターンを削除"""
    if not text:
        return text

    # 日付パターンのリスト
    # 2022.12.21◎, 2023.11.18, 2016.4.28/2021.5.17/ 2022.12.24◎ など
    patterns = [
        r'\d{4}\.\d{1,2}\.\d{1,2}[^,\n]*?◎',  # 日付+◎
        r'\d{4}\.\d{1,2}\.\d{1,2}[/\s]*',     # 日付+スラッシュ/スペース
        r'\d{4}\.l\d{1,2}\.\d{1,2}[/\s]*',    # タイポ対応 (l→1)
        r'\d{4},\d{1,2}\.\d{1,2}[/\s]*',      # タイポ対応 (,→.)
        r'\d{4}\.\d{1,2},\d{1,2}[/\s]*',      # タイポ対応 (,→.)
        r'\d{4}\.l\d{1,2},\d{1,2}[/\s]*',     # タイポ対応
        r'\d{4}\.\d{1,2}[/\s]*',              # 不完全な日付
        r'\d{4},\d{1,2}[/\s]*',               # 不完全な日付(タイポ)
        r'\d{4}\.l\d{1,2}[/\s]*',             # 不完全な日付(タイポ)
        r'\d{2}19\.9\.\d{1,2}[/\s]*',        # タイポ対応
        r'\d{4}\s*\.?\s*\d{1,2}\s*\.?\s*\d{1,2}',  # 柔軟なパターン
    ]

    result = text
    for pattern in patterns:
        result = re.sub(pattern, '', result)

    # 連続するスペースや記号を整理
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'^[\s/]+|[\s/]+$', '', result)

    return result.strip()


def clean_csv(input_file, output_file):
    """CSVファイルから日付を削除"""
    cleaned_rows = []

    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            # 現代語訳から日付を削除
            if '現代語訳' in row:
                row['現代語訳'] = remove_dates(row['現代語訳'])

            # 原文_ルビ付きからも念のため削除
            if '原文_ルビ付き' in row:
                row['原文_ルビ付き'] = remove_dates(row['原文_ルビ付き'])

            cleaned_rows.append(row)

    # 新しいCSVファイルに書き出し
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    print(f"完了: {len(cleaned_rows)} 行のデータをクリーニングしました")
    print(f"出力ファイル: {output_file}")


if __name__ == '__main__':
    input_file = 'genji_monogatari.csv'
    output_file = 'genji_monogatari_cleaned.csv'

    clean_csv(input_file, output_file)

    # サンプル表示
    print("\n=== クリーニング後のサンプル ===")
    with open(output_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i < 5:
                print(f"\n行 {i+1}:")
                print(f"  原文: {row['原文_ルビ付き'][:50]}...")
                print(f"  現代語訳: {row['現代語訳'][:50]}...")
            else:
                break
