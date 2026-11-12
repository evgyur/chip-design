#!/usr/bin/env python3
"""Bounded DesignBookmark motion catalog; copy endpoints explicitly offered by its UI."""
import argparse
import datetime as dt
import fcntl
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

SOURCE = 'https://designbookmark.com/motion'


class Cards(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.card = None
        self.paragraph = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        a = {key: (value or '') for key, value in attrs}
        if tag == 'li' and 'scroll-mt-6' in a.get('class', '').split() and a.get('id'):
            if self.card:
                raise ValueError('nested motion card')
            self.card = {'id': a['id'], 'labels': [], 'links': [], 'anchor_title': ''}
        if self.card:
            if tag == 'a' and a.get('href', '').startswith('https://'):
                self.paragraph = True
                self.parts = []
            if tag == 'p':
                self.paragraph = True
                self.parts = []
            if tag == 'a' and a.get('href', '').startswith('https://'):
                u = urlsplit(a['href'])
                self.card['links'].append(urlunsplit((u.scheme, u.netloc, u.path, '', '')))

    def handle_data(self, data):
        if self.card and self.paragraph:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag in ('p', 'a') and self.card and self.paragraph:
            self.card['labels'].append(' '.join(''.join(self.parts).split()))
            self.paragraph = False
        if tag == 'li' and self.card:
            self.cards.append(self.card)
            self.card = None


def parse(text):
    parser = Cards()
    parser.feed(text)
    result = []
    for row in parser.cards:
        ident = row['id']
        if not re.fullmatch(r'[a-z0-9-]{1,100}', ident):
            raise ValueError('invalid card identity')
        if len(row['labels']) < 2:
            raise ValueError('missing title/provider')
        result.append({'id': ident, 'name': row['labels'][0], 'provider': row['labels'][1],
                       'source_page': SOURCE + '#' + ident,
                       'upstream_url': next(iter(row['links']), None),
                       'copy_url': 'https://designbookmark.com/motion-src/code/' + ident + '.txt'})
    if not 1 <= len(result) <= 300 or len({r['id'] for r in result}) != len(result):
        raise ValueError('empty/oversized/duplicate catalog')
    # The rendered card inventory must match the site's ItemList fragments.
    declared = set(re.findall(r'https://designbookmark\.com/motion#([a-z0-9-]+)', text))
    if declared and declared != {r['id'] for r in result}:
        raise ValueError('structured/rendered item coverage mismatch')
    return result


def fetch(url, limit=2_000_000):
    req = Request(url, headers={'User-Agent': 'ChipDesignCatalog/1.0 (bounded personal reference collection)'})
    with urlopen(req, timeout=25) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('source response too large')
    return data


def atomic(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.new')
    temporary.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    os.replace(temporary, path)


def refresh(root, download=False):
    root.mkdir(parents=True, exist_ok=True)
    with (root / '.refresh.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        old = json.loads((root / 'catalog.json').read_text()) if (root / 'catalog.json').exists() else None
        rows = parse(fetch(SOURCE).decode())
        oldrows = {r['id']: r for r in old['items']} if old else {}
        old_receipts = {r['id']: r for r in old.get('copies', [])} if old else {}
        added = [r for r in rows if r['id'] not in oldrows]
        changed = [r for r in rows if r['id'] in oldrows and r != oldrows[r['id']]]
        removed = sorted(set(oldrows) - {r['id'] for r in rows})
        copies = list(old_receipts.values())
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        # Persist a complete validated index first; an interrupted import remains explicitly incomplete.
        packet = {'source': SOURCE, 'checked_at': now, 'count': len(rows), 'items': rows, 'copies': copies,
                  'removed_ids': sorted(set((old or {}).get('removed_ids', [])) | set(removed))}
        atomic(root / 'catalog.json', packet)
        if download:
            copydir = root / 'copies'
            copydir.mkdir(exist_ok=True)
            for row in rows:
                target = copydir / (row['id'] + '.txt')
                previous = old_receipts.get(row['id'])
                if previous and target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == previous['sha256']:
                    continue
                time.sleep(10)  # site's robots.txt crawl-delay, including page -> first copy
                data = fetch(row['copy_url'])
                if len(data) < 50 or b'<!DOCTYPE html><html' in data[:100] and b'404' in data[:1000]:
                    raise ValueError('missing/invalid code copy: ' + row['id'])
                target.write_bytes(data)
                record = {'id': row['id'], 'file': 'copies/' + target.name, 'sha256': hashlib.sha256(data).hexdigest(),
                          'bytes': len(data), 'retrieved_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                          'source_url': row['copy_url'], 'reuse_status': 'author-provided copy; verify license/assets before distribution'}
                copies = [r for r in copies if r['id'] != row['id']] + [record]
                packet['copies'] = copies
                atomic(root / 'catalog.json', packet)
        # New entries remain indexed and visibly pending import during metadata-only periodic checks.
        packet['pending_copy_ids'] = [r['id'] for r in rows if r['id'] not in {c['id'] for c in copies}]
        atomic(root / 'catalog.json', packet)
        delta = {'checked_at': now, 'added': added, 'changed': changed, 'removed': removed,
                 'count': len(rows), 'copies': len(copies), 'pending_copy_ids': packet['pending_copy_ids']}
        atomic(root / 'last-check.json', delta)
        return delta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()
    try:
        delta = refresh(args.root, args.download)
        if not args.quiet and (delta['added'] or delta['changed'] or delta['removed']):
            lines = [f"DesignBookmark Motion: новых {len(delta['added'])}, изменённых {len(delta['changed'])}, исчезнувших {len(delta['removed'])}. Каталог: {delta['count']} элементов."]
            for row in delta['added'] + delta['changed']:
                lines.append(f"┈ {row['name']} ({row['provider']}) — {row['source_page']}")
            if delta['pending_copy_ids']:
                lines.append('Новые записи проиндексированы; исходники новых элементов ещё требуют импорта и проверки перед использованием.')
            print('\n'.join(lines))
    except Exception as exc:
        # Do not misclassify source/parser failure as empty/unchanged catalog.
        print('Не удалось проверить DesignBookmark Motion: ' + type(exc).__name__ + '. Последний подтверждённый каталог сохранён.', file=__import__('sys').stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
