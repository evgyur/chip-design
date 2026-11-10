#!/usr/bin/env python3
"""Local-only Dembrandt invocation; no account sync, session import or CDP attachment."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlsplit


def command(args):
    url = urlsplit(args.url)
    if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password:
        raise ValueError('an explicit HTTP(S) URL without embedded credentials is required')
    runtime = args.runtime.resolve()
    package = runtime / 'node_modules/dembrandt'
    if json.loads((package / 'package.json').read_text())['version'] != '0.39.2':
        raise ValueError('runtime must be pinned to dembrandt 0.39.2')
    node = shutil.which('node')
    if not node:
        raise ValueError('Node.js is required')
    result = [node, str(package / 'dist/index.js'), args.url, '--json-only', '--no-headed-fallback']
    for name, flag in (('mobile', '--mobile'), ('dark_mode', '--dark-mode'), ('wcag', '--wcag'), ('dtcg', '--dtcg'), ('design_md', '--design-md')):
        if getattr(args, name):
            result.append(flag)
    if args.compare:
        baseline = args.compare.resolve(strict=True)
        if not baseline.is_file():
            raise ValueError('comparison requires an existing local baseline file, never a cloud baseline ID')
        result += ['--compare', str(baseline)]
    env = {k: v for k, v in os.environ.items() if k not in ('DEMBRANDT_KEY', 'BROWSER_CDP_ENDPOINT')}
    env['DEMBRANDT_NO_HEADED_FALLBACK'] = '1'
    return result, env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    parser.add_argument('--runtime', type=Path, required=True, help='isolated npm prefix containing pinned Dembrandt')
    parser.add_argument('--output-dir', type=Path, required=True)
    for name in ('mobile', 'dark-mode', 'wcag', 'dtcg', 'design-md'):
        parser.add_argument('--' + name, action='store_true')
    parser.add_argument('--compare', type=Path)
    args = parser.parse_args()
    try:
        cmd, env = command(args)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(cmd, cwd=args.output_dir.resolve(), env=env, timeout=180)
        return result.returncode
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        parser.exit(2, f'local Dembrandt failed: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
