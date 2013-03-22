class Bookmarks(object):
    
    def __init__(self, conn=None):
        """
           receive connection from Tornado Application
        """
        self.conn = conn

    def insert(self, bookmark):
        insert_stmt = """
                        INSERT INTO 
                            bookmarks (name, description, url, user_id, published, updated) 
                        VALUES (%s, %s, %s, 1, UTC_TIMESTAMP(), UTC_TIMESTAMP())
                      """
        return self.conn.execute(insert_stmt, bookmark['name'], bookmark['description'], bookmark['url'])

    def all(self):
        """
            retrieve all bookmarks
            TODO: paginate this query
        """    
        return self.conn.query("SELECT * FROM bookmarks ORDER BY published DESC")

    def delete(self, bookmark_id):
        """
            remove a bookmark by id
        """
        bookmark = self.get_by_id(bookmark_id)
        if not bookmark: raise RecordNotFound
        
        return self.conn.execute("DELETE FROM bookmarks WHERE id = (%s)", int(bookmark_id))

    def get_by_id(self, bookmark_id):
        """
            retrieve a label by id
        """
        return self.conn.get("SELECT * FROM bookmarks WHERE id = %s", int(bookmark_id))

class Labels(object):

    def __init__(self, conn=None):
        """
           receive connection from Tornado Application
        """
        self.conn = conn

    def get_or_insert(self, label_name):
        """
            retrieve a label or insert one if there is no label for name informed
        """	
        label = self.conn.get("SELECT * FROM labels WHERE name = %s", label_name)
        
        if not label:  		      
            rowid = self.conn.execute(
                "INSERT INTO labels (name) VALUES (%s)", label_name)
            label = self.conn.get("SELECT * FROM labels WHERE id = %s", int(rowid))

        return label
    
    def get_by_id(self, label_id):
        """
            retrieve a label by id
        """
        return self.conn.get("SELECT * FROM labels WHERE id = %s", int(label_id))

    def all(self):
        """
            retrieve all labels
        """	
        return	self.conn.query("SELECT * FROM labels")

    def count(self):
        """
            count all labels
        """	
        return	self.conn.execute_rowcount("SELECT * FROM labels")

    def delete(self, label_id):
        """
            remove a label by id
        """	
        return self.conn.execute("DELETE FROM labels WHERE id = (%s)", int(label_id))
    
class RecordNotFound(Exception):
    pass
