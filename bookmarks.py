class Bookmarks(object):
    pass



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
    
    def get_by_id(self, id):
        """
            retrieve a label by id
        """
        return self.conn.get("SELECT * FROM labels WHERE id = %s", int(id))

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

    def remove(self, id):
        """
            remove a label by id
        """	
        return self.conn.execute(
                "DELETE FROM labels WHERE id = (%s)", int(id))