from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Setup the Database for populating
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

####### GET HANDLERS ########
    def do_GET(self):
        try:
            # ADD A NEW RESTAURANT
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<html><body><h3>Add a Restaurant</h3>"

                output += "<form method='POST' enctype='multipart/form-data' " \
                      "action='/restaurants/new'><h2>Enter Restaurant Name:" \
                      "</h2><input name='name' type='text'><input " \
                      "type='submit' value='Submit'></form></body></html>"
                self.wfile.write(output)
                print output
                return

            # UPDATE/EDIT A RESTAURANT
            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                restaurantQuery = session.query(Restaurant). \
                    filter_by(id = restaurantIDPath).one()

                if restaurantQuery != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = "<html><body><h3>Edit %s</h3>" % restaurantQuery.name

                    output += "<form method='POST' enctype='multipart/form-data' " \
                          "action='/restaurants/%s/edit'>" % restaurantIDPath
                    output += "</h2><input name='newName' type='text'" \
                            " value='%s'><input " % restaurantQuery.name
                    output += "type='submit' value='Rename'></form></body></html>"
                    self.wfile.write(output)
                    print output
                return

            # DELETE A RESTAURANT
            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                restaurantQuery = session.query(Restaurant). \
                    filter_by(id = restaurantIDPath).one()

                if restaurantQuery != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = "<html><body><h3>Delete %s</h3>" % restaurantQuery.name

                    output += "<form method='POST' enctype='multipart/form-data' " \
                          "action='/restaurants/%s/delete'>" % restaurantIDPath
                    output += "<h4>Are you sure you want to delete %s?" % \
                              restaurantQuery.name
                    output += "</h4><input " \
                              "type='submit' value='Delete'></form></body></html>"
                    self.wfile.write(output)
                    print output
                return

            # MAIN RESTAURANTS LIST / SELECT
            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant)\
                    .order_by(Restaurant.name).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                new = self.path + "/new"
                output = "<html><body><a href='%s'>Add New Restaurant</a>" % new

                for restaurant in restaurants:
                    output += "<h3>%s</h3>" % restaurant.name
                    output += "<a href='/restaurants/%s/edit'>Edit</a>" % restaurant.id
                    output += "<a href='/restaurants/%s/delete'>Delete</a>" % restaurant.id
                output += "<form method='POST' enctype='multipart/form-data' " \
                      "action='/hello'><h2>What would you like me to say?" \
                      "</h2><input name='message' type='text'><input " \
                      "type='submit' value='Submit'></form></body></html>"
                self.wfile.write(output)
                print output
                return

            # ERROR ON 404
            else:
                self.send_error(404, "File Not Found %s" % self.path)

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

####### POST HANDLERS #######
    def do_POST(self):
        try:
            # ADD A NEW RESTAURANT
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                restaurant = fields.get('name')

                add = Restaurant(name = restaurant[0])
                session.add(add)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            # EDIT A RESTAURANT
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newName')
                    restaurantIDPath = self.path.split("/")[2]
                    restaurantQuery = session.query(Restaurant). \
                        filter_by(id = restaurantIDPath).one()

                    if restaurantQuery != []:
                        restaurantQuery.name = messagecontent[0]
                        session.add(restaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

            # DELETE A RESTAURANT
            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                restaurantQuery = session.query(Restaurant). \
                    filter_by(id = restaurantIDPath).one()

                if restaurantQuery != []:
                    session.delete(restaurantQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

        except:
            pass

def main():
    try:
        port = 8000
        server = HTTPServer(('',port), WebServerHandler)
        print "Web server is running on port %s..." % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()