#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
源氏物語スクレイパー
http://james.3zoku.com/genji/ から原文と現代語訳を取得してCSVに保存
"""

import urllib.request
import ssl
import csv
import json
import re
from bs4 import BeautifulSoup, NavigableString
from typing import List, Dict, Tuple

# SSL証明書検証を無効化
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.check_verify_mode = False


def fetch_html(url: str) -> str:
    """URLからHTMLを取得"""
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ssl_context) as response:
        return response.read().decode('utf-8', errors='ignore')


def extract_text_with_ruby(element) -> str:
    """ルビ付きテキストを抽出（ルビを括弧で表記）"""
    result = []
    for content in element.descendants:
        if isinstance(content, NavigableString):
            text = str(content).strip()
            if text and content.parent.name not in ['rt', 'rp']:
                result.append(text)
        elif content.name == 'ruby':
            base = content.find(text=True, recursive=False)
            rt = content.find('rt')
            if base and rt:
                base_text = str(base).strip()
                rt_text = rt.get_text().strip()
                if base_text and rt_text:
                    result.append(f"{base_text}({rt_text})")
    return ''.join(result)


def extract_plain_text(element) -> str:
    """プレーンテキストを抽出（リンクとルビを除去）"""
    # ルビタグの処理
    for ruby in element.find_all('ruby'):
        # ルビの本文のみを残す
        base_text = ruby.find(text=True, recursive=False)
        if base_text:
            ruby.replace_with(base_text)
        else:
            ruby.decompose()

    # リンクタグの処理（テキストのみを残す）
    for a in element.find_all('a'):
        if not a.get('id'):  # idを持つものは残す
            a.replace_with(a.get_text())

    return element.get_text().strip()


def extract_links(element) -> List[Dict[str, str]]:
    """用語説明へのリンクを抽出"""
    links = []
    for a in element.find_all('a', href=True):
        href = a['href']
        if 'genji_term' in href:
            text = a.get_text()
            links.append({
                'text': text,
                'href': href
            })
    return links


def split_into_sentences(text: str) -> List[str]:
    """テキストを文単位に分割"""
    # 句点で分割（。で終わる文）
    sentences = []
    current = []

    # まず改行で分割
    paragraphs = text.split('\n')

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # 句点で分割
        parts = re.split(r'([。」』])', para)

        for i in range(0, len(parts), 2):
            if i < len(parts):
                sentence = parts[i]
                if i + 1 < len(parts):
                    sentence += parts[i + 1]
                sentence = sentence.strip()
                if sentence:
                    current.append(sentence)

                    # 句点で終わっている場合は文として確定
                    if sentence.endswith(('。', '」', '』')):
                        sentences.append(''.join(current))
                        current = []

    # 残りがあれば追加
    if current:
        sentences.append(''.join(current))

    return [s.strip() for s in sentences if s.strip()]


def parse_genji_page(html: str, volume_num: int, volume_name: str) -> List[Dict]:
    """源氏物語のHTMLをパースしてデータを抽出"""
    soup = BeautifulSoup(html, 'html.parser')
    data = []

    # メインテーブルを取得（3つ目以降のテーブル）
    tables = soup.find_all('table')
    if len(tables) < 3:
        return data

    # 本文テーブルは3つ目から
    main_table = None
    for table in tables[2:]:
        # class属性がないテーブルを探す
        if not table.get('class'):
            main_table = table
            break

    if not main_table:
        return data

    rows = main_table.find_all('tr')

    current_section_id = ""
    current_section_name = ""

    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue

        original_cell = cells[0]
        modern_cell = cells[1]

        # セクションヘッダーの検出
        section_header = original_cell.find('strong')
        if section_header:
            # セクションIDと名前を抽出
            section_link = section_header.find('a', id=True)
            if section_link:
                current_section_id = section_link.get('id', '')
                # セクション名はIDの後のテキスト
                section_text = section_header.get_text()
                # "1.1　父帝と母桐壺更衣の物語" から "父帝と母桐壺更衣の物語" を抽出
                parts = section_text.split('　', 1)
                if len(parts) > 1:
                    current_section_name = parts[1].strip()
                else:
                    current_section_name = section_text.strip()
            continue

        # 本文の抽出
        # strongタグがあればスキップ（ヘッダー行）
        if original_cell.find('strong'):
            continue

        # 原文の処理
        original_copy = BeautifulSoup(str(original_cell), 'html.parser')
        original_plain = extract_plain_text(original_copy)

        original_copy2 = BeautifulSoup(str(original_cell), 'html.parser')
        original_ruby = extract_text_with_ruby(original_copy2)

        original_links = extract_links(original_cell)

        # 現代語訳の処理
        modern_text = modern_cell.get_text().strip()

        # <br>タグで段落分割されている場合を考慮
        original_paragraphs = str(original_cell).split('<br>')
        modern_paragraphs = str(modern_cell).split('<br>')

        # 段落ごとに処理
        for orig_para_html, mod_para_html in zip(original_paragraphs, modern_paragraphs):
            orig_soup = BeautifulSoup(orig_para_html, 'html.parser')
            mod_soup = BeautifulSoup(mod_para_html, 'html.parser')

            # プレーンテキスト
            orig_plain = extract_plain_text(BeautifulSoup(str(orig_soup), 'html.parser'))
            # ルビ付き
            orig_ruby = extract_text_with_ruby(orig_soup)
            # リンク
            orig_links = extract_links(orig_soup)

            mod_text = mod_soup.get_text().strip()

            # 原文と現代語訳を文単位に分割
            orig_sentences = split_into_sentences(orig_ruby)
            mod_sentences = split_into_sentences(mod_text)

            # 文の数を合わせる（現代語訳の方が少ない場合が多い）
            max_len = max(len(orig_sentences), len(mod_sentences))

            for i in range(max_len):
                orig_sent = orig_sentences[i] if i < len(orig_sentences) else ""
                mod_sent = mod_sentences[i] if i < len(mod_sentences) else ""

                if orig_sent or mod_sent:
                    data.append({
                        '巻番号': volume_num,
                        '巻名': volume_name,
                        'セクションID': current_section_id,
                        'セクション名': current_section_name,
                        '文番号': i + 1,
                        '原文_ルビ付き': orig_sent,
                        '原文_リンク情報': json.dumps(orig_links, ensure_ascii=False) if orig_links else "",
                        '現代語訳': mod_sent
                    })

    return data


def main():
    """メイン処理"""
    base_url = 'http://james.3zoku.com/genji/'

    # 巻の情報（番号と名前）
    volumes = [
        (1, '桐壺'), (2, '帚木'), (3, '空蝉'), (4, '夕顔'), (5, '若紫'),
        (6, '末摘花'), (7, '紅葉賀'), (8, '花宴'), (9, '葵'), (10, '賢木'),
        (11, '花散里'), (12, '須磨'), (13, '明石'), (14, '澪標'), (15, '蓬生'),
        (16, '関屋'), (17, '絵合'), (18, '松風'), (19, '薄雲'), (20, '朝顔'),
        (21, '乙女'), (22, '玉鬘'), (23, '初音'), (24, '胡蝶'), (25, '蛍'),
        (26, '常夏'), (27, '篝火'), (28, '野分'), (29, '行幸'), (30, '藤袴'),
        (31, '真木柱'), (32, '梅枝'), (33, '藤裏葉'), (34, '若菜上'), (35, '若菜下'),
        (36, '柏木'), (37, '横笛'), (38, '鈴虫'), (39, '夕霧'), (40, '御法'),
        (41, '幻'), (42, '匂兵部卿'), (43, '紅梅'), (44, '竹河'), (45, '橋姫'),
        (46, '椎本'), (47, '総角'), (48, '早蕨'), (49, '宿木'), (50, '東屋'),
        (51, '浮舟'), (52, '蜻蛉'), (53, '手習'), (54, '夢浮橋')
    ]

    all_data = []

    for vol_num, vol_name in volumes:
        print(f"巻{vol_num:02d} {vol_name} を取得中...")

        url = f"{base_url}genji{vol_num:02d}.html"

        try:
            html = fetch_html(url)
            data = parse_genji_page(html, vol_num, vol_name)
            all_data.extend(data)
            print(f"  → {len(data)} 件のデータを取得")
        except Exception as e:
            print(f"  → エラー: {e}")

    # CSVに出力
    output_file = 'genji_monogatari.csv'
    if all_data:
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['巻番号', '巻名', 'セクションID', 'セクション名', '文番号',
                          '原文_ルビ付き', '原文_リンク情報', '現代語訳']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_data)

        print(f"\n完了: {len(all_data)} 件のデータを {output_file} に保存しました")
    else:
        print("\nデータが取得できませんでした")


if __name__ == '__main__':
    main()
