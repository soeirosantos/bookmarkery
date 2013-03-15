import os

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.database

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_database", default="bookmarkery_db", help="database name")
define("mysql_user", default="root", help="database user")
define("mysql_password", default="", help="database password")


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
        ]
        
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )

        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = tornado.database.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)

    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
