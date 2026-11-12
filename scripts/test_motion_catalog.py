"""DesignBookmark parser and delta tests use isolated fixtures/state, no network."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('motion_catalog', Path(__file__).with_name('motion_catalog.py'))
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
NATIVE = '<li id="db-demo" class="scroll-mt-6"><p>Demo</p><p>DesignBookmark</p></li>'
LINKED = '<li id="dial" class="scroll-mt-6"><a href="https://kokonutui.com/docs/dial?ref=x">Dial</a><p>Kokonut UI</p></li>'


class MotionCatalog(unittest.TestCase):
    def test_native_and_linked_complete(self):
        rows = M.parse(NATIVE + LINKED)
        self.assertEqual([r['name'] for r in rows], ['Demo', 'Dial'])
        self.assertEqual(rows[1]['upstream_url'], 'https://kokonutui.com/docs/dial')
        self.assertTrue(rows[0]['copy_url'].endswith('/db-demo.txt'))

    def test_empty_and_duplicate_fail(self):
        for text in ('<html>offline</html>', NATIVE + NATIVE):
            with self.assertRaises(ValueError):
                M.parse(text)

    def test_declared_item_missing_fails(self):
        with self.assertRaisesRegex(ValueError, 'coverage'):
            M.parse(NATIVE + 'https://designbookmark.com/motion#missing')

    def test_delta_quiet_and_additions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(M, 'fetch', return_value=NATIVE.encode()):
                first = M.refresh(root)
                second = M.refresh(root)
            self.assertEqual(len(first['added']), 1)
            self.assertFalse(second['added'] or second['changed'] or second['removed'])
            with patch.object(M, 'fetch', return_value=(NATIVE + LINKED).encode()):
                third = M.refresh(root)
            self.assertEqual([r['id'] for r in third['added']], ['dial'])
            self.assertEqual(third['pending_copy_ids'], ['db-demo', 'dial'])
            before = (root / 'catalog.json').read_bytes()
            with patch.object(M, 'fetch', return_value=b'unavailable'):
                with self.assertRaises(ValueError):
                    M.refresh(root)
            self.assertEqual((root / 'catalog.json').read_bytes(), before)

    def test_copy_resumable_and_hash_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = b'<!-- Author example -->\n' + b'const a = 1;\n' * 10
            def request(url):
                return NATIVE.encode() if url == M.SOURCE else code
            with patch.object(M, 'fetch', side_effect=request) as fetch, patch.object(M.time, 'sleep'):
                result = M.refresh(root, True)
                self.assertFalse(result['pending_copy_ids'])
                fetch.reset_mock()
                M.refresh(root, True)
                self.assertEqual(fetch.call_count, 1)  # page only; verified copy reused
            self.assertEqual((root / 'copies/db-demo.txt').read_bytes(), code)


if __name__ == '__main__':
    unittest.main()
