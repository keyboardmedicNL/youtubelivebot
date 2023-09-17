# loads libraries needed in script
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json

#variables used in script
configcheck=False

# loads config into variables for use in script
while configcheck == False: # loop to ensure config gets loaded
    try:
        with open("config/config.json") as config: # opens config and stores data in variables
            configJson = json.load(config)
            hostName = configJson["hostname"]
            serverPort = int(configJson["webport"])
            config.close()
            configcheck = True # stops loop if succesfull
            print("<WEBSERVER> Succesfully loaded config") # log message
    except Exception as e: # catches exception
        print("<WEBSERVER> An exception occurred whilst trying to load the config:", str(e)) # log message
        print("<WEBSERVER> trying again in 1 minute") # log message
        time.sleep(60)

# start webserver
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>Hello, i am a webserver.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("<WEBSERVER> Server started http://%s:%s" % (hostName, serverPort)) # log messaage


    webServer.serve_forever()