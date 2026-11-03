#!/usr/bin/env python3
"""Validate source gitlinks; --metadata-only explicitly skips checkout checks."""
import argparse
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'design-taste-frontend', 'gpt-taste', 'superdesign-skill', 'better-design',
            'design-taste', 'canvas-ui', 'shaders', 'uilayouts', 'hyperiux-components',
            'motion-primitives', 'cursify', 'trickle-UI-kit', 'stageshow'}


def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', '-C', str(cwd), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata-only', action='store_true')
    args = parser.parse_args()
    pins = dict(re.findall(r'\| `([^`]+)` `([0-9a-f]{40})` \|',
                           (ROOT / 'references/source-modules.md').read_text()))
    assert len(pins) == 11, 'expected eleven modern manifest pins'
    entries = {}
    for line in git('ls-files', '--stage', 'upstreams').splitlines():
        mode, sha, stage, path = line.split()
        assert mode == '160000' and stage == '0', 'source is not a clean gitlink'
        entries[Path(path).name] = (sha, path)
    assert set(entries) == EXPECTED, 'missing or unexpected source gitlinks'
    for name, (sha, path) in entries.items():
        if name in pins:
            assert pins[name] == sha, f'pin mismatch: {name}'
        url = git('config', '-f', '.gitmodules', '--get', f'submodule.{path}.url')
        assert re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git', url), path
        if not args.metadata_only:
            target = ROOT / path
            assert (target / '.git').exists(), f'uninitialized source: {path}'
            assert git('rev-parse', 'HEAD', cwd=target) == sha, path
            assert not git('status', '--porcelain', cwd=target), f'dirty source: {path}'
    root = (ROOT / 'SKILL.md').read_text()
    assert 'Do not select Refero or call its API' in root
    assert 'Hallmark' in root and 'Elaya' in root and 'Never invent proof' in root
    assert '/home/' not in root, 'nonportable operator path'
    for link in re.findall(r'\]\(([^)]+)\)', root):
        if '://' not in link:
            assert (ROOT / link).is_file(), f'missing reference: {link}'
    label = 'gitlink/manifest metadata only; checkouts NOT exercised' if args.metadata_only else 'gitlinks, pins and initialized clean checkouts'
    print(f'PASS: 13 sources (2 legacy + 11 modern); {label}; router contracts')


if __name__ == '__main__':
    main()
