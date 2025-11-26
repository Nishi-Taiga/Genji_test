#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用語解説ページから全ての用語定義を取得してJSONに保存
"""

import urllib.request
import ssl
import json
from bs4 import BeautifulSoup

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.check_verify_mode = False

def fetch_term_definitions(term_file_num):
    """指定された用語ファイルから定義を取得"""
    url = f'http://james.3zoku.com/genji/genji_term{term_file_num:02d}.html'
    print(f'取得中: {url}')

    req = urllib.request.Request(url)

    try:
        with urllib.request.urlopen(req, context=ssl_context) as response:
            html = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f'  エラー: {e}')
        return {}

    soup = BeautifulSoup(html, 'html.parser')

    definitions = {}

    # IDを持つ全てのa要素を探す
    term_anchors = soup.find_all('a', id=True)

    for anchor in term_anchors:
        term_id = anchor.get('id')

        # このアンカーの親div
        parent_div = anchor.parent

        if parent_div and parent_div.name == 'div':
            # 次のdivを探す（これが解説内容）
            next_div = parent_div.find_next_sibling('div')

            if next_div:
                # strongタグから用語名を取得
                strong = next_div.find('strong')
                term_name = strong.get_text().strip() if strong else ''

                # 解説文全体を取得
                definition_text = next_div.get_text().strip()

                definitions[term_id] = {
                    'id': term_id,
                    'name': term_name,
                    'definition': definition_text,
                    'file': f'genji_term{term_file_num:02d}.html'
                }

    print(f'  → {len(definitions)} 件の用語を取得')
    return definitions

def main():
    """メイン処理"""
    all_definitions = {}

    # 用語ファイルは01から54まで（巻の数と同じ）
    for i in range(1, 55):
        definitions = fetch_term_definitions(i)
        all_definitions.update(definitions)

    # JSONファイルに保存
    output_file = 'genji_term_definitions.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_definitions, f, ensure_ascii=False, indent=2)

    print(f'\n完了: {len(all_definitions)} 件の用語定義を {output_file} に保存しました')

    # JavaScriptファイルとしても保存
    js_file = 'genji_term_definitions.js'
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write('const genjiTerms = ')
        json.dump(all_definitions, f, ensure_ascii=False, indent=2)
        f.write(';')

    print(f'JavaScript版も保存: {js_file}')

if __name__ == '__main__':
    main()
