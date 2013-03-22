import os

try:
    server_port = os.environ['OPENSHIFT_INTERNAL_PORT']
    server_ip   = address = os.environ['OPENSHIFT_INTERNAL_IP']
    db_name     = "bookmarkery"
    db_port     = os.environ['OPENSHIFT_MYSQL_DB_PORT']
    db_host     = os.environ['OPENSHIFT_MYSQL_DB_HOST']
    db_user     = os.environ['OPENSHIFT_MYSQL_DB_USERNAME']
    db_passwd   = os.environ['OPENSHIFT_MYSQL_DB_PASSWORD']

    virtenv = os.environ['OPENSHIFT_HOMEDIR'] + 'python-2.6/virtenv/tornadoenv/'
    virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
    execfile(virtualenv, dict(__file__=virtualenv))
    debug = False


except KeyError:
    server_port = 8888
    server_ip   = "127.0.0.1"
    db_name     = "bookmarkery_db"
    db_port     = 3306
    db_host     = "127.0.0.1"
    db_user     = "root"
    db_passwd   = ""
    debug = True

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.database

from tornado.options import define, options
from bookmarks import Bookmarks, RecordNotFound

define("port", default=server_port, help="run on the given port", type=int)
define("ip", default=server_ip, help="run on the given ip")
define("mysql_host", default=":".join((db_host, str(db_port))), help="database host")
define("mysql_database", default=db_name, help="database name")
define("mysql_user", default=db_user, help="database user")
define("mysql_password", default=db_passwd, help="database password")
define("debug", default=debug, help="debugging option")


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/add", AddHandler),
            (r"/delete", DeleteHandler),
        ]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=options.debug,
        )

        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = tornado.database.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        bookmarks = Bookmarks(self.application.db).all()
        self.render("index.html", bookmarks=bookmarks)

class AddHandler(tornado.web.RequestHandler):
    def get(self):
        bookmarks = Bookmarks(self.application.db).all()
        self.render("index.html", bookmarks=bookmarks)

    def post(self):
        bookmark = dict(
                          name=self.get_argument("name", None),
                          url=self.get_argument("url", None),
                          description=self.get_argument("description", None)
                        )
        if bookmark['url']:
            Bookmarks(self.application.db).insert(bookmark)
        
        self.redirect("/")

class DeleteHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            bookmark_id = self.get_argument("id", None)
            Bookmarks(self.application.db).delete(bookmark_id)
            self.redirect("/")
        except RecordNotFound:
            raise tornado.web.HTTPError(404)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port, address=options.ip)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()