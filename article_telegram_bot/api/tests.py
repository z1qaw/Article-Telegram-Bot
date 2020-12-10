from unittest import TestCase, main as ut_main
from unittest import result

import requests

from .services.arabianbusiness import ArabianBusinessParser
from .services.bbc import BbcParser
from .services.inosmi import InoSmiParser
from .services.iransegodnya import IranTodayParser
from .services.lenta import LentaParser
from .services.reuters import ReutersParser


class TestArabianBusinessService(TestCase):
    def test_get_latest(self):
        parser = ArabianBusinessParser(requests.session())
        self.assertTrue(parser.get_latest())

    def test_get_article(self):
        parser = ArabianBusinessParser(requests.session())
        self.assertTrue(parser.get_article(
            '/property/454156-will-dubais-virtual-visa-deliver-post-coronavirus-boost-to-the-real-estate-market'))


class TestBbcService(TestCase):
    def test_get_latest(self):
        parser = BbcParser(requests.session())
        self.assertTrue(parser.get_latest())

    def test_get_article(self):
        parser = BbcParser(requests.session())
        self.assertTrue(parser.get_article('/news/uk-england-humber-54986043'))


class TestInoSmiService(TestCase):
    def test_get_latest(self):
        parser = InoSmiParser(requests.session())
        self.assertTrue(parser.get_latest())

    def test_get_article(self):
        parser = InoSmiParser(requests.session())
        self.assertTrue(parser.get_article('/social/20201118/248569557.html'))


class TestIranTodayService(TestCase):
    def test_get_latest(self):
        parser = IranTodayParser(requests.session())
        self.assertTrue(parser.get_latest())

    def test_get_article(self):
        parser = IranTodayParser(requests.session())
        self.assertTrue(parser.get_article('/post/view/3787'))


class TestLentaService(TestCase):
    def test_get_latest(self):
        parser = LentaParser(requests.session())
        result = parser.get_latest()
        print(result)
        self.assertTrue(result)

    def test_get_article(self):
        parser = LentaParser(requests.session())
        self.assertTrue(parser.get_article('/post/view/3787'))


class TestReutersService(TestCase):
    def test_get_latest(self):
        parser = ReutersParser(requests.session())
        result = parser.get_latest()
        print(result)
        self.assertTrue(result)


if __name__ == '__main__':
    ut_main(warnings='ignore')
