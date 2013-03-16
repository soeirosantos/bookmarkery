import unittest

import tornado.database

from labels import Labels

class IntegrationTest(unittest.TestCase):

    def setUp(self):
        self.conn = tornado.database.Connection(
	        host="/opt/lampp/var/mysql/mysql.sock", database="bookmarkery_db_test",
            user="root", password="")

    def tearDown(self):
        self.conn.execute("truncate table labels")
        self.conn.execute("truncate table bookmarks")


    def get_labels(self):
        return Labels(self.conn)

    def test_get_or_insert_label(self):
        first_label_name = "Python"
        result_label = self.get_labels().get_or_insert(first_label_name)	

        assert first_label_name == result_label.name
        
        total_before_insert = self.get_labels().count()     
        another_result_label = self.get_labels().get_or_insert(first_label_name)
        total_after_insert = self.get_labels().count()     

        the_same_total = total_before_insert == total_after_insert

        the_same_label = result_label.id == another_result_label.id

        assert the_same_total and the_same_label 

    def test_remove_label(self):
        label_name = "Trip"
        result_label = self.get_labels().get_or_insert(label_name)    	
        
        removed_id = self.get_labels().remove(result_label.id)

        label = self.get_labels().get_by_id(removed_id)

        assert label == None

    def test_insert_bookmark(self):
        


if __name__ == "__main__":
    unittest.main()