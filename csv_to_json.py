#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSVをJSONに変換してHTMLに埋め込みやすくする
"""

import csv
import json

def csv_to_json(csv_file, json_file):
    """CSVをJSONに変換"""
    data = []

    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # 空のデータをスキップ
            if not row['原文_ルビ付き'] or not row['現代語訳']:
                continue

            data.append({
                'volumeNum': int(row['巻番号']) if row['巻番号'] else 0,
                'volumeName': row['巻名'],
                'sectionId': row['セクションID'],
                'sectionName': row['セクション名'],
                'sentenceNum': int(row['文番号']) if row['文番号'] else 0,
                'original': row['原文_ルビ付き'],
                'links': row['原文_リンク情報'],
                'translation': row['現代語訳']
            })

    # JSONファイルに保存
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"完了: {len(data)} 件のデータを {json_file} に保存しました")

    # JavaScriptファイルとしても保存（変数として埋め込み）
    js_file = json_file.replace('.json', '.js')
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write('const genjiData = ')
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write(';')

    print(f"JavaScript版も保存: {js_file}")

if __name__ == '__main__':
    csv_to_json('genji_monogatari.csv', 'genji_data.json')
