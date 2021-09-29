# A modified version of https://gist.github.com/Blackburn29/126dccf185e4bb2276dc#file-fbauth-py

import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from http.server import BaseHTTPRequestHandler, HTTPServer
from base64 import urlsafe_b64encode

PORT = 3000
REDIRECT_URI = f"http://localhost:{PORT}/"


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, address, server, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        super().__init__(request, address, server)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if "code" in self.path:
            self.wfile.write(b"<html><body><p>OK got it, now you may close this window</p></body></html>")
            auth_token = urlsafe_b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {auth_token}"}
            req = Request("https://accounts.spotify.com/api/token", data=urlencode({
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
                "code": self.path.split("=")[1],
            }).encode(), headers=headers)
            res = json.loads(
                urlopen(req).read().decode()
            )  # contains access and refresh tokens
            self.server.access_token = res.get("access_token")

    def log_request(self, format, *args):
        return


class SpotifyAuthHandler:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_access_token(self, scopes):
        print(f"Open this URL in your browser:\nhttps://accounts.spotify.com/authorize?client_id={self.client_id}&response_type=code&scope={scopes}&redirect_uri={REDIRECT_URI}")
        server = HTTPServer(
            ("localhost", PORT),
            lambda request, address, server: RequestHandler(
                request, address, server, self.client_id, self.client_secret
            )
        )
        server.socket.settimeout(60)
        print("waiting 1 minutes for the confirmation...")
        server.handle_request()
        return server.access_token if hasattr(server, "access_token") else None


client_id = input("Enter your client id: ")
client_secret = input("Enter your client secret: ")
confirm = input("Do you want to generate oauth2 access token (y/n): ").lower()
if confirm != "y":
    exit("Ok bei")

while True:
    redirect_con = input(f"Have you set redirect uri ({REDIRECT_URI}) in your app dashboard (y/n): ").lower()
    if redirect_con == "y":
        break
    else:
        print("cannot continue without that so do it")

while True:
    scopes = input("Enter the scopes of this auth seperated by commas (https://spoti.fi/3zWVebK): ")
    if scopes:
        break

auth = SpotifyAuthHandler(client_id, client_secret)
access_token = auth.get_access_token(scopes)
print(f"Access token: {access_token if access_token else 'not found'}")
