from tornado.database import Row
import itertools

class Bookmarks(object):
    
    def __init__(self, conn=None):
        """
           receive connection from Tornado Application
        """
        self.conn = conn
        self.labels = Labels(conn)

    def insert(self, bookmark):
        insert_stmt = """
                        INSERT INTO 
                            bookmarks (name, description, url, user_id, published, updated) 
                        VALUES (%s, %s, %s, 1, UTC_TIMESTAMP(), UTC_TIMESTAMP())
                      """
        
        bookmark_rowid = self.conn.execute(insert_stmt, bookmark['name'], bookmark['description'], bookmark['url'])
        
        if bookmark['labels']:
            for label in bookmark['labels'].split(","):
                label = self.labels.get_or_insert(label)
                self.associate_label(bookmark_rowid, label['id'])

        return bookmark_rowid

    def all(self):
        """
            retrieve all bookmarks
            TODO: paginate this query
        """    
        
        query = """
                    SELECT b.*
                          ,l.id as label_id
                          ,l.name as label_name 
                    FROM bookmarks b 
                         LEFT JOIN bookmarks_labels bl 
                             on b.id = bl.bookmark_id 
                         LEFT JOIN labels l 
                                 on l.id = bl.label_id 
                    ORDER BY b.published DESC
                """
        
        results = self.conn.query(query)
        
        bookmarks_hash = {}
        bookmarks = []
        
        for result in results:
            if bookmarks_hash.has_key(result['id']):
                bookmarks_hash[result['id']].labels.append( Row(itertools.izip( ['id', 'name'], [ result['label_id'], result['label_name'] ] )) )
            else:
                bookmark = Row(itertools.izip(['id', 'name', 'url', 'description', 'published', 'labels']
                                             ,[result['id'], result['name'], result['url'], result['description'], result['published'], [] ]))
                if result['label_id']:
                    bookmark.labels.append( Row(itertools.izip( ['id', 'name'], [ result['label_id'], result['label_name'] ] )) )
                
                bookmarks.append(bookmark)
                bookmarks_hash[result['id']] = bookmark
        
        return bookmarks

    def delete(self, bookmark_id):
        """
            remove a bookmark by id
        """
        bookmark = self.get_by_id(bookmark_id)
        if not bookmark: raise RecordNotFound
        
        self.conn.execute("DELETE FROM bookmarks_labels WHERE bookmark_id = (%s)", int(bookmark_id))
        return self.conn.execute("DELETE FROM bookmarks WHERE id = (%s)", int(bookmark_id))

    def get_by_id(self, bookmark_id):
        """
            retrieve a bookmark by id
        """
        return self.conn.get("SELECT * FROM bookmarks WHERE id = %s", int(bookmark_id))

    def validate(self, bookmark):
        messages = []
        if not bookmark['url']:
            messages.append("sounds good provide a url here...")
            
        return messages
    
    def is_associated(self, bookmark_id, label_id):
        return self.conn.get("SELECT * FROM bookmarks_labels WHERE bookmark_id = %s AND label_id = %s", int(bookmark_id), int(label_id))
    
    def associate_label(self, bookmark_id, label_id):
        associated = self.is_associated(bookmark_id, label_id)
        if not associated:
            self.conn.execute(
                       "INSERT INTO bookmarks_labels (bookmark_id, label_id) VALUES (%s, %s)", bookmark_id, label_id)
    
    def disassociate_label(self, bookmark_id, label_id):
        associated = self.is_associated(bookmark_id, label_id)
        if associated:
            self.conn.execute(
                       "DELETE FROM bookmarks_labels WHERE bookmark_id = %s AND label_id = %s", bookmark_id, label_id)
                
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
        assert label_name
        
        label_name = label_name.strip()
        
        label = self.conn.get("SELECT * FROM labels WHERE LOWER(name) = %s", label_name.lower())
        
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
        label = self.get_by_id(label_id)
        if not label: raise RecordNotFound

        self.conn.execute("DELETE FROM bookmarks_labels WHERE label_id = (%s)", int(label_id))
        return self.conn.execute("DELETE FROM labels WHERE id = (%s)", int(label_id))
    
class RecordNotFound(Exception):
    pass

class CustomRow(dict):
    """
        A dict that allows for object-like property access syntax.
        copied from tornado.database.Row
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)