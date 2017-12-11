import unittest
from fin_project import *

class Headline_Tests(unittest.TestCase):
    def setUp(self):
        self.url_rs = "https://www.redstate.com"
        try:
            self.data_rs = open("redstate.html", 'r').text
        except:
            self.data_rs = get_html_from_url(self.url_rs)
            f = open("redstate.html", 'w')
            f.write(self.data_rs)
            f.close()

        self.url_itt = "http://inthesetimes.com/top/P9"
        try:
          self.data_itt = open("inthesetimes.html",'r').text
        except:
          self.data_itt = get_html_from_url(self.url_itt)
          f = open("inthesetimes.html",'w')
          f.write(self.data_itt)
          f.close()

    def test_url(self):
        self.assertTrue("http://" in self.url_itt, "Testing that a correct URL has been entered.")

    def test_html(self):
        self.assertTrue(len(self.data_itt) != 0, "Testing that HTML was scraped from the Internet.")

    def test_html_two(self):
        self.assertTrue(len(self.data_rs) != 0, "Testing that HTML was scraped from the Internet.")

    def test_cache(self):
        testfile = open(CACHE_FNAME,'r')
        tfstr = testfile.read()
        testfile.close()
        self.assertTrue(len(tfstr) != 0, "Testing that there is info in the cache.")

    def test_soup(self):
        func_test = inthesetimes_stories_html(self.data_itt)
        self.assertTrue(len(func_test) > 1, "Testing that the function has correctly returned an object.")

    def test_soup_two(self):
        func_test = inthesetimes_stories_html(self.data_itt)
        func_test_two = inthesetimes_story_list(func_test)
        self.assertTrue(type(func_test_two) == type([]), "Testing that the function has correctly returned a list.")

    def test_soup_three(self):
        func_test = redstate_stories_html(self.data_rs)
        self.assertTrue(len(func_test) > 1, "Testing that the function has correctly returned an object.")

    def test_soup_four(self):
        func_test = redstate_stories_html(self.data_rs)
        func_test_two = redstate_story_list(func_test)
        self.assertTrue(type(func_test_two) == type([]), "Testing that the function has correctly returned a list.")

class Database_Test(unittest.TestCase):
    def setUp(self):
        self.db_connection, self.db_cursor = None, None
        self.db_connection, self.db_cursor = get_connection_and_cursor()

    def test_database_connection(self):
        self.assertNotEqual(type(self.db_connection), type(self.db_cursor))

class SQL_Query_Test(unittest.TestCase):
    def setUp(self):
        sql = 'SELECT * FROM "headlines"'
        db_cursor.execute(sql)
        self.headlines = db_cursor.fetchall()

    def test_sql(self):
        self.assertTrue(type(self.headlines) == type([]), "Testing that the query has returned a list.")

    def test_sql_two(self):
        test_dict = {"key": "lock", "door": "hinge"}
        self.assertTrue(type(self.headlines[0].keys()) == type(test_dict.keys()), "Testing that the SQL query has returned an object with keys.")

class Headline_Class_Test(unittest.TestCase):
    def setUp(self):
        story_obj = {
            'id': 168,
            'title': 'Building an Alternative to Capitalism From the Ground Up',
            'author': ' Dayton Martindale',
            'site_id': 168,
            'url': '/article/20665/Capitalism-economic-democracy-solidarity-economy',
            'name': 'inthesetimes'
        }
        self.class_obj = Headline(story_obj)

    def test_headline_one(self):
        self.assertTrue(self.class_obj.site == "inthesetimes", "Testing that the class instance returns the correct site.")

    def test_headline_two(self):
        self.assertEqual(self.class_obj.__str__(), 'Building an Alternative to Capitalism From the Ground Up by  Dayton Martindale [inthesetimes]', "Testing the class string method works.")

    def test_headline_three(self):
        self.assertEqual(self.class_obj.__repr__(), "<class 'fin_project.Headline'>('Building an Alternative to Capitalism From the Ground Up')", "Testing that the class __repr__ method works.")

    def test_headline_four(self):
        self.assertTrue(self.class_obj.__contains__("Capitalism") == 'Building an Alternative to Capitalism From the Ground Up', "Testing that the class contains method works.")
        self.assertTrue(self.class_obj.__contains__("Trump") == None)



if __name__ == "__main__":
    unittest.main(verbosity=2)
