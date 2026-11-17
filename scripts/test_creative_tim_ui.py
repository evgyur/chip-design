"""Focused routing/source tests. No application backend or rendering is exercised."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('verify_modules', ROOT / 'scripts/verify-modules.py')
assert SPEC is not None and SPEC.loader is not None
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)
PIN = '20eb87b1f671a2ba778b435c53249522080e8f27'


class CreativeTimUiIntegration(unittest.TestCase):
    def test_live_pin_and_source_files(self):
        path = ROOT / 'upstreams/creative-tim-ui'
        sha = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
        self.assertEqual(sha, PIN)
        for name in ('LICENSE.md', 'README.md', 'package.json',
                     'skills/creative-tim-ui/AGENTS.md',
                     'skills/creative-tim-ui/rules/tailwind-rules.md',
                     'apps/www/registry/creative-tim/blocks/account-basic-info-01/page.tsx',
                     'apps/www/public/r/account-basic-info-01.json'):
            self.assertTrue((path / name).is_file(), name)
        self.assertIn('MIT License', (path / 'LICENSE.md').read_text())

    def test_pinned_registry_has_free_content_and_no_mcp(self):
        path = ROOT / 'upstreams/creative-tim-ui'
        registry = (path / 'apps/www/registry.json').read_text()
        self.assertNotIn('"pro"', registry)
        items = sorted((path / 'apps/www/public/r').glob('*.json'))
        self.assertGreaterEqual(len(items), 170)
        self.assertFalse([p for p in path.rglob('*mcp*') if '.git' not in p.parts])

    def test_routing_and_contracts(self):
        root = (ROOT / 'SKILL.md').read_text()
        text = (ROOT / 'references/creative-tim-ui.md').read_text()
        self.assertIn('references/creative-tim-ui.md', root)
        combined = text + (ROOT / 'references/source-modules.md').read_text()
        for needle in ('Hallmark', 'approved brand', 'no PRO content', 'no MCP server shipped',
                       'not a visual direction', 'stale', 'hydration', 'hot-linked',
                       'static demo', 'npx @creative-tim/ui@latest'):
            self.assertIn(needle, combined)

    def test_portable_verifier(self):
        with patch.object(sys, 'argv', ['verify-modules.py']):
            VERIFIER.main()

    def test_bad_gitlink_rejected_without_mutating_checkout(self):
        original = VERIFIER.git

        def corrupted(*args, **kwargs):
            result = original(*args, **kwargs)
            return result.replace(PIN, '0' * 40) if args == ('ls-files', '--stage', 'upstreams') else result

        with patch.object(VERIFIER, 'git', corrupted), patch.object(sys, 'argv', ['verify-modules.py', '--metadata-only']):
            with self.assertRaisesRegex(AssertionError, 'pin mismatch: creative-tim-ui'):
                VERIFIER.main()


if __name__ == '__main__':
    unittest.main()
