from http.server import BaseHTTPRequestHandler, HTTPServer
import pandas as pd
import time
import markdown as md
import jinja2 as jj
import yaml
from sys import argv
from pathlib import Path
import os
import glob
from datetime import date
import mimetypes
from urllib.parse import unquote


# Open the file and load the file
with open('_site.yml') as f:
    sitedict = yaml.safe_load(f)


hostName = "localhost"
serverPort = 8080

df = pd.read_csv("central.csv", keep_default_na = False).tail(100)
try:
    static = pd.read_csv("static.csv")
except:
    static = None
endpoints = set(df["endpoint"])
static_endpoints = set(static["endpoint"]) if static is not None else set([])
templates = {}
templateLoader = jj.FileSystemLoader(searchpath="_layouts")
templateEnv = jj.Environment(loader=templateLoader)
templateEnv.globals["now"] = date.today()
for temp_name in set(df["template"]):
    templates[temp_name] = templateEnv.get_template(temp_name + ".html")


pages = []
for _, page in df.iterrows():
    try:
        with open(page["dir"] + page["filename"], "r") as fin:
            page["content"] = fin.read()
    except:
        page["content"] = ""
    pages += [dict(page)]
sitedict["pages"] = pages
#del pages

data = {}
for filename in glob.glob("_data/*"):
    file_ext = filename.split(".")[-1]
    proper_filename = filename.split("/")[-1][:-len(file_ext)-1]
    if file_ext == "csv":
        data[proper_filename] = pd.read_csv(filename, keep_default_na=False).to_dict('records')
    elif file_ext == "yml":
        with open(filename, "r") as fin:
            data[proper_filename] = yaml.safe_load(fin) 

sitedict["data"] = data
sitedict["materialfolder_files"] = glob.glob(sitedict["materialfolder"]+"/**/*", recursive=True)



class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.path = unquote(self.path)
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
            
            try:
                with open(page["dir"] + page["filename"], "r") as fin:
                    content = fin.read()
            except:
                content = ""
                
            template = templateEnv.get_template(page["template"] + ".html")
            page["content"] = md.markdown(content)
            self.wfile.write(bytes(template.render({"page": page, "site": sitedict}), "utf-8"))
            
        elif self.path in static_endpoints:
            self.send_response(200)
            if self.path.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            self.send_header('Content-type', mimetypes.guess_type(self.path))
            self.end_headers()
            info = static[static["endpoint"]==self.path].iloc[0]
            with open(info["dir"] + info["filename"], "rb") as fin:
                self.wfile.write(fin.read())
        
        ## try to render anyway
        elif os.path.isfile("."+self.path):
            self.send_response(200)
            self.send_header('Content-type', mimetypes.guess_type(self.path))
            self.end_headers()
            with open("."+self.path, "rb") as fin:
                self.wfile.write(fin.read())
            




        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(f'<html><head><meta http-equiv="refresh" content="0; URL=/404"></head><body></body></html>', "utf-8"))

def treat_central(page, output_folder = "_site"):
    if page["endpoint"].endswith("/"):
        page["endpoint"] += "index.html"
    try:
        with open(page["dir"] + page["filename"], "r") as fin:
            content = fin.read()
    except:
        content = ""
    template = templateEnv.get_template(page["template"] + ".html")
    page["content"] = md.markdown(content)
    filename = output_folder + page["endpoint"]
    Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
    with open(filename, "w+") as fout:
        fout.write(template.render({"page": page, "site": sitedict}))


def treat_static(info, output_folder = "_site"):
    with open(info["dir"] + info["filename"], "rb") as fin:
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
        if static is not None:
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
