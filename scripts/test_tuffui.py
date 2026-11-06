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
PIN = '16389fad9d3ac87d94e061cd4a1ae287b1864123'


class TuffuiIntegration(unittest.TestCase):
    def test_live_pin_and_source_files(self):
        path = ROOT / 'upstreams/tuffui'
        sha = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
        self.assertEqual(sha, PIN)
        for name in ('README.md', 'LICENSE', 'package.json', 'lib/catalog.ts',
                     'registry/tool-approval-queue/docs.ts',
                     'registry/tool-approval-queue/tool-approval-queue.tsx'):
            self.assertTrue((path / name).is_file(), name)
        self.assertIn('MIT License', (path / 'LICENSE').read_text())

    def test_routing_and_contracts(self):
        root = (ROOT / 'SKILL.md').read_text()
        text = (ROOT / 'references/tuffui.md').read_text()
        self.assertIn('references/tuffui.md', root)
        for needle in ('Hallmark', 'Elaya', 'Stageshow', 'Ordinary landing pages',
                       'UI is not backend authorization', 'No API subscription',
                       'Default to the existing backend', 'authoritative acknowledgment',
                       'Undo', 'registry/use-mock-run/', 'DEMO', 'approved brand',
                       'reduced motion', 'Focused acceptance'):
            # Some invariants are expressed in the source catalog rather than the bridge.
            combined = text + (ROOT / 'references/source-modules.md').read_text()
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
            with self.assertRaisesRegex(AssertionError, 'pin mismatch: tuffui'):
                VERIFIER.main()


if __name__ == '__main__':
    unittest.main()
