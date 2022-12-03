from http.server import BaseHTTPRequestHandler, HTTPServer
import pandas as pd
import time
import markdown as md
import jinja2 as jj
import yaml
from sys import argv
from pathlib import Path
import os


# Open the file and load the file
with open('_site.yml') as f:
    sitedict = yaml.safe_load(f)


hostName = "localhost"
serverPort = 8080

df = pd.read_csv("central.csv", keep_default_na = False)
static = pd.read_csv("static.csv")
endpoints = set(df["endpoint"])
static_endpoints = set(static["endpoint"])
templates = {}
templateLoader = jj.FileSystemLoader(searchpath="_layouts")
templateEnv = jj.Environment(loader=templateLoader)
for temp_name in set(df["template"]):
    templates[temp_name] = templateEnv.get_template(temp_name + ".html")


pages = []
for _, page in df.iterrows():
    with open(page["folder"] + page["filename"], "r") as fin:
        page["content"] = fin.read()
        pages += [dict(page)]
sitedict["pages"] = pages
#del pages

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("index.html"):
            self.path = self.path[:-10]
        if self.path in endpoints:
            self.send_response(200)
            if self.path.endswith(".json"):
                self.send_header("Content-type", "application/json")
            else:
                self.send_header("Content-type", "text/html")
            self.end_headers()
            
            #with open('_site.yml') as f:
            #    sitedict = yaml.safe_load(f)
            
            page = df[df["endpoint"]==self.path].iloc[0]
            
            with open(page["folder"] + page["filename"], "r") as fin:
                content = fin.read()
            
            template = templateEnv.get_template(page["template"] + ".html")
            page["content"] = md.markdown(content)
            self.wfile.write(bytes(template.render({"page": page, "site": sitedict}), "utf-8"))
            
        elif self.path in static_endpoints:
            self.send_response(200)
            if self.path.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            elif self.path.endswith('.json'):
                self.send_header('Content-type', 'application/javascript')
            elif self.path.endswith('.js'):
                self.send_header('Content-type', 'application/javascript')
            elif self.path.endswith('.ico'):
                self.send_header('Content-type', 'image/x-icon')
            elif self.path.endswith('.png'):
                self.send_header('Content-type', 'image/png')
            else:
                self.send_header('Content-type', 'text/html')
            self.end_headers()
            info = static[static["endpoint"]==self.path].iloc[0]
            with open(info["folder"] + info["filename"], "rb") as fin:
                self.wfile.write(fin.read())
            
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(f'<html><head><meta http-equiv="refresh" content="0; URL=/404"></head><body></body></html>', "utf-8"))

def treat_central(page, output_folder = "_site"):
    if page["endpoint"].endswith("/"):
        page["endpoint"] += "index.html"
    with open(page["folder"] + page["filename"], "r") as fin:
        content = fin.read()
    template = templateEnv.get_template(page["template"] + ".html")
    page["content"] = md.markdown(content)
    filename = output_folder + page["endpoint"]
    Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
    with open(filename, "w+") as fout:
        fout.write(template.render({"page": page, "site": sitedict}))


def treat_static(info, output_folder = "_site"):
    with open(info["folder"] + info["filename"], "rb") as fin:
        filename = output_folder + info["endpoint"]
        Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
        with open(filename, "wb+") as fout:
            fout.write(fin.read())


if __name__ == "__main__":
    if len(argv) > 1 and argv[1]=="build":
        output_folder = "_site"
        if len(argv) > 2:
            output_folder = argv[2]
        df.apply(treat_central, output_folder = output_folder, axis = 1)
        static.apply(treat_static, output_folder = output_folder, axis = 1)
    else:
        webServer = HTTPServer((hostName, serverPort), MyServer)
        print(f"Server started http://{hostName}:{serverPort}")

        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass

        webServer.server_close()
        print("Server stopped.")
