import unittest

from x_fulltext_fetcher.fetch import parse_status_url


class UrlParsingTest(unittest.TestCase):
    def test_parse_x_status_url(self):
        self.assertEqual(parse_status_url("https://x.com/example/status/123?s=46"), ("example", "123"))

    def test_parse_twitter_status_url(self):
        self.assertEqual(parse_status_url("https://twitter.com/example/status/456"), ("example", "456"))

    def test_parse_fxtwitter_status_url(self):
        self.assertEqual(parse_status_url("https://api.fxtwitter.com/example/status/789"), ("example", "789"))


if __name__ == "__main__":
    unittest.main()
