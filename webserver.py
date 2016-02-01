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

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body><h3>Add a Restaurant</h3>"

                output += "<form method='POST' enctype='multipart/form-data' " \
                      "action='/restaurants/new'><h2>Enter Restaurant Name:" \
                      "</h2><input name='name' type='text'><input " \
                      "type='submit' value='Submit'></form></body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant)\
                    .order_by(Restaurant.name).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                new = self.path + "/new"
                output = ""
                output += "<html><body><a href='%s'>Add New Restaurant</a>" % new

                for restaurant in restaurants:
                    output += "<h3>%s</h3>" % restaurant.name
                    output += "<a href='#'>Edit</a> <a href='#'>Delete</a>"
                output += "<form method='POST' enctype='multipart/form-data' " \
                      "action='/hello'><h2>What would you like me to say?" \
                      "</h2><input name='message' type='text'><input " \
                      "type='submit' value='Submit'></form></body></html>"
                self.wfile.write(output)
                print output
                return

            else:
                self.send_error(404, "File Not Found %s" % self.path)

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
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

                #output = ""
                #output += "<html><body>"
                #output += " <h2> %s has been added!: </h2>" % restaurant[0]
                #output += "<a href='/restaurants'>Back to Restaurants</a>" \
                #          "</body></html>"
                #self.wfile.write(output)
                #print output

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