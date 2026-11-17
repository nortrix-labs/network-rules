import unittest
import build


class FeedTests(unittest.TestCase):
    def test_suffix_deduplication(self):
        self.assertEqual(build.consolidate({'ads.example.com', 'example.com', 'other.example.net'}, set()), ['example.com', 'other.example.net'])

    def test_protected_child_removes_broad_parent_block(self):
        self.assertEqual(build.consolidate({'example.com', 'api.example.com', 'ad.example.net'}, {'api.example.com'}), ['ad.example.net'])

    def test_protected_suffix_preserves_sibling_blocks(self):
        self.assertEqual(build.consolidate({'api.good.example', 'good.example', 'bad.example'}, {'good.example'}), ['bad.example'])

    def test_surge_policies_and_commands_cannot_enter_feed(self):
        for raw in (b'DOMAIN-SUFFIX,example.com,DIRECT', b'[General]', b'URL-REGEX,.*', b'RULE-SET,https://example.com'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                build.parse(raw, 'surge')

    def test_domains_only_syntax_and_injection(self):
        self.assertEqual(build.parse(b'# comment\n*.Ads.Example.com\n', 'domains'), {'ads.example.com'})
        for raw in (b'<html>error</html>', b'0.0.0.0', b'localhost', b'example.com,REJECT', b'a..example.com'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                build.parse(raw, 'domains')

    def test_domain_boundaries(self):
        self.assertEqual(build.consolidate({'notclaude.ai', 'claude.ai'}, {'claude.ai'}), ['notclaude.ai'])

    def test_bad_counts_keep_previous_feed(self):
        for count in (0, 69999, 150001):
            with self.subTest(count=count), self.assertRaises(ValueError):
                build.check_size('test', count, 100000, 100)
        build.check_size('test', 100000, 100000, 100)


if __name__ == '__main__':
    unittest.main()
