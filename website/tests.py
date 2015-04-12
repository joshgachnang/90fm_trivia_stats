from django.test import TestCase
import mock
import urllib2

from website import models


class ScraperTestCase(TestCase):

    def setUp(self):
        self.html = open('website/test_data/2014_hour54_scores.html',
                         'r')
        self.scraper = models.Scraper()

    def test_sanitize_team_name(self):
        name = 'a&#160;&amp;b&quot;c&nbsp;d'
        self.assertEqual('a &b"c d', models.sanitize_team_name(name))

    @mock.patch.object(models, 'current_year')
    @mock.patch.object(models, 'post_to_twitter')
    @mock.patch('website.models.Scraper.scrape_year_hour')
    @mock.patch.object(models, 'remaining_hours')
    @mock.patch.object(models, 'during_trivia')
    def test_scrape(self, during_mock, hours_mock, scrape_mock, post_mock,
                    year_mock):
        during_mock.return_value = True
        hours_mock.return_value = [52, 53, 54]
        year_mock.return_value = 2015

        scrape_mock.side_effect = [False, True]

        self.scraper.scrape()

        scrape_mock.assert_has_calls = [
            mock.call(2015, 52),
            mock.call(2015, 53)
        ]
        post_mock.assert_called_once_with(mock.ANY)

    @mock.patch.object(models, 'current_year')
    @mock.patch.object(models, 'post_to_twitter')
    @mock.patch('website.models.Scraper.scrape_year_hour')
    @mock.patch.object(models, 'remaining_hours')
    @mock.patch.object(models, 'during_trivia')
    def test_scrape_no_new_hours(self, during_mock, hours_mock, scrape_mock,
                                 post_mock, year_mock):
        during_mock.return_value = True
        hours_mock.return_value = [52, 53, 54]
        year_mock.return_value = 2015

        scrape_mock.side_effect = [False, False, False]

        self.scraper.scrape()

        scrape_mock.assert_has_calls = [
            mock.call(2015, 52),
            mock.call(2015, 53),
            mock.call(2015, 54)
        ]
        self.assertFalse(post_mock.called)

    @mock.patch.object(models, 'current_year')
    def test_remaining_hours(self, year_mock):
        year_mock.return_value = 2015

        models.Score(team_name='test1', year=2015, hour=1,
                     place=1, score=1000).save()
        models.Score(team_name='test2', year=2015, hour=1,
                     place=2, score=500).save()
        models.Score(team_name='test1', year=2015, hour=8,
                     place=1, score=2000).save()
        models.Score(team_name='test2', year=2015, hour=8,
                     place=2, score=1000).save()

        expected = ['09'] + [str(i) for i in range(10, 54)]

        self.assertEqual(expected, models.remaining_hours())

    @mock.patch('urllib2.urlopen')
    def test_get_page(self, url_mock):
        url_mock.return_value = 'test'

        self.assertEqual('test', self.scraper.get_page(2013, 1))

        url_mock.assert_called_once_with(
            'http://90fmtrivia.org/TriviaScores2013/scorePages/results.htm')

    @mock.patch('urllib2.urlopen')
    def test_get_page_hour54(self, url_mock):
        url_mock.return_value = 'test'

        self.assertEqual('test', self.scraper.get_page(2014, 54))

        url_mock.assert_called_once_with(
            'http://90fmtrivia.org/TriviaScores2014/scorePages/results.html')

    @mock.patch('urllib2.urlopen')
    def test_get_page_old(self, url_mock):
        url_mock.return_value = 'test'

        self.assertEqual('test', self.scraper.get_page(2012, 1))

        url_mock.assert_called_once_with(
            'http://90fmtrivia.org/TriviaScores2012/scorePages/results1.htm')

    @mock.patch('urllib2.urlopen')
    def test_get_page_fail(self, url_mock):
        url_mock.side_effect = urllib2.HTTPError('url', 500, '', '',
                                                 mock.Mock())

        self.assertFalse(self.scraper.get_page(2012, 54))

        url_mock.assert_has_calls([
            mock.call('http://90fmtrivia.org/TriviaScores2012/scorePages/'
                      'results54.htm'),
            mock.call('http://90fmtrivia.org/TriviaScores2012/scorePages/'
                      'results.htm')])

    @mock.patch('website.models.Scraper.get_page')
    def test_scrape_year_hour(self, page_mock):
        page_mock.return_value = self.html

        self.scraper.scrape_year_hour(2014, 54)

        self.assertEqual(371, models.Score.objects.all().count())
