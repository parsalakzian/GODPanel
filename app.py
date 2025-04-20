import argparse
import json
import os
import shutil
import time
import zipfile
from flask import Flask , render_template, send_file, redirect, session, url_for, request
from api import SanaeiAPI
from database import Database
from zipfile import ZipFile
  
if os.path.exists(os.path.join("static")) == False:
    os.mkdir(os.path.join("static"))

if os.path.exists(os.path.join("static", "qrcodes")) == False:
    os.mkdir(os.path.join("static", "qrcodes"))

app = Flask(__name__)
app.secret_key = 'abcd12344321dcba'
  
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))



@app.route('/') 
def index(): 
    if "UUID" in session and "username" in session:
        try: 
            db = Database()
            server = db.get_servers().get("data")[0]
            sn = SanaeiAPI(server.get("username"), server.get("password"), server.get("url"))
            admin_inbound_id = db.get_admins_inbound_id(session.get("UUID"))["data"]["inbound_id"]
            dd = sn.get_admin_clients(admin_inbound_id, session.get("UUID"))
            print(dd)
            if dd.get("status"):
                d = dd["data"]["clients"]
                onlines = dd["data"]["onlines"]
                expiryes = dd["data"]["expiryes"]
            
            
                data = {"admin_id": session.get("UUID"), "username": session.get("username"), "configs": d, "total": len(d), "online": onlines, "expired": expiryes, "new": db.get_new().get("data")["new"], "wallet": f"{db.get_admins_wallet(session["UUID"]).get("data")["wallet"]:,}", "next_user":f"{session["username"]}{len(d)+1}"}
                return render_template("main.html", data=data)
            else:
                return render_template("error.html", error=dd["error"])
        except Exception as e:
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            error_message = f"{str(e)} (File: {file_name}, Line: {exc_tb.tb_lineno})"
            return render_template("error.html", error=error_message)
    elif "username" in session and "UUID" not in session:
        return redirect(url_for("admin"))
    else:
        return redirect(url_for("login"))

@app.route('/admin') 
def admin(): 
    if "username" in session and "UUID" not in session:
        try:
            db = Database()
            server = db.get_servers().get("data")
            if len(server) > 0:
                sn = SanaeiAPI(server[0].get("username"), server[0].get("password"), server[0].get("url"))
                dda = sn.login()
                if (dda["status"]):
                    
                    d = []
                    admins = db.get_admins()["data"]
                    
                    if len(server) > 0:
                        da = sn.get_inbounds()["data"]
                    else:
                        da = []
                    
                    for admin in admins:
                        dd = db.get_admins_configs(admin["id"])
                        d.append({
                            "admin_id":admin["id"],
                            "username":admin["username"],
                            "password":admin["password"],
                            "inbound":[item["remark"] for item in da if item["id"] == admin["inbound_id"]][0],
                            "inbound_id":admin["inbound_id"],
                            "wallet":f"{int(admin["wallet"]):,}",
                            "int_wallet":admin["wallet"],
                            "total":len(dd["data"]),
                        })
                    
                    data = {"admin_id": session.get("UUID"), "admins": d, "new": db.get_new().get("data")["new"], "inbounds": json.dumps(da), "server_status":True}
                    
                else:
                    data = {"admin_id": session.get("UUID"), "admins": [], "new": db.get_new().get("data")["new"], "inbounds": [], "server_status":False}
            
            else:
                data = {"admin_id": session.get("UUID"), "admins": [], "new": db.get_new().get("data")["new"], "inbounds": [], "server_status":False}
                
            return render_template("admin.html", data=data)
        
        except Exception as e:
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            error_message = f"{str(e)} (File: {file_name}, Line: {exc_tb.tb_lineno})"
            return render_template("error.html", error=error_message)
        
    else:
        return redirect(url_for("login"))    

@app.route('/login', methods=['GET', 'POST']) 
def login(): 
    if request.method == "GET":
        if "username" in session:
            return redirect(url_for("index"))
        else:
            return render_template("login.html")
    else:
        usernames = ["padmin"]
        passwords = ["padmin"]
        
        with open(os.path.join("admin.json"), "r") as f:
            data = json.loads(f.read())
            
        usernames.append(data["username"])
        passwords.append(data["password"])
        
        username = request.form.get("username")
        password = request.form.get("password")
        if username in usernames and password in passwords:
            session["username"] = username
            return redirect(url_for("admin"))
        db = Database()
        res = db.login_admin(username, password)
        if res["status"]:
            session["UUID"] = res["data"]["id"]
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", message=res["error"])
    
@app.route('/renew', methods=['GET', 'POST']) 
def renew(): 
    if request.method == "GET":
        if "username" in session:
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    else:
        try:
            if "username" in session:
                data = json.loads(request.get_data())
                username = data.get("username")
                inbound_id = data.get("inbound_id")
                user_id = data.get("user_id")
                
                db = Database()
                server = db.get_servers()["data"][0]
                sn = SanaeiAPI(server["username"], server["password"], server["url"])
                
                wallet = db.get_admins_wallet(session["UUID"])["data"]["wallet"]
                if wallet >= 60000:
                
                    d = sn.update_client(int(inbound_id), user_id, username)
                    print(d)
                    d = sn.reset_client_traffic(inbound_id, username)
                    print(d)
                    db.add_admin_wallet(session.get("UUID"), -60000)
                    
                    return {"status":True}
                else :
                    return {"status":False, "error":"Your wallet is Low"}
            else:
                return {"status":False, "error":"You are not logged in"}
        except Exception as e:
            return {"status":False, "error":str(e)}
    
@app.route('/new', methods=['GET', 'POST']) 
def new(): 
    if request.method == "GET":
        if "username" in session:
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    else:
        try:
            if "username" in session:
                data = json.loads(request.get_data())
                username = data.get("username")
                
                
                
                db = Database()
                server = db.get_servers()["data"][0]
                sn = SanaeiAPI(server["username"], server["password"], server["url"])
                
                wallet = db.get_admins_wallet(session["UUID"])["data"]["wallet"]
                if wallet >= 60000:
                    inbound_id = int(db.get_admins_inbound_id(session["UUID"])["data"]["inbound_id"])
                    d = sn.add_client(inbound_id, username, session["UUID"])
                    if d["status"] ==False:
                        return {"status":False, "error":d["error"]}
                    
                    # dd = db.add_config(d["id"], username, inbound_id, session["UUID"])
                    # if dd["status"] ==False:
                    #     return {"status":False, "error":dd["error"]}
                    
                    db.add_admin_wallet(session.get("UUID"), -60000)
                    
                    return {"status":True}
                else :
                    return {"status":False, "error":"Your wallet is Low"}
            else:
                return {"status":False, "error":"You are not logged in"}
        except Exception as e:
            return {"status":False, "error":str(e)}
        
@app.route('/download/<name>') 
def download(name): 
    try:
        if "username" in session:
            return send_file(os.path.join("static", "qrcodes", name+".png"), as_attachment=True)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        return render_template("error.html", error=str(e))
    
@app.route('/new_admin', methods=['GET', 'POST']) 
def new_admin(): 
    if request.method == "GET":
        if "username" in session:
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    else:
        try:
            if "username" in session and "UUID" not in session:
                data = json.loads(request.get_data())
                username = data.get("username")
                password = data.get("password")
                inbound_id = data.get("inbound_id")
                
                db = Database()
                
                d = db.add_admin(username, password, inbound_id)
                if d["status"] == False:
                    return d
                
                return {"status":True}
            else:
                return {"status":False, "error":"You are not logged in"}
        except Exception as e:
            return {"status":False, "error":str(e)}
    
@app.route('/edit_admin', methods=['GET', 'POST']) 
def edit_admin(): 
    if request.method == "GET":
        if "username" in session:
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    else:
        try:
            if "username" in session and "UUID" not in session:
                data = json.loads(request.get_data())
                username = data.get("username")
                password = data.get("password")
                inbound_id = data.get("inbound_id")
                
                db = Database()
                
                d = db.edit_admin(username, password, inbound_id)
                if d["status"] == False:
                    return d
                
                return {"status":True}
            else:
                return {"status":False, "error":"You are not logged in"}
        except Exception as e:
            return {"status":False, "error":str(e)}
    
@app.route('/new_news', methods=['GET', 'POST']) 
def new_news(): 
    if request.method == "GET":
        if "username" in session:
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    else:
        try:
            if "username" in session and "UUID" not in session:
                data = json.loads(request.get_data())
                new = data.get("new")
                
                db = Database()
                d = db.add_new(new)
                if d["status"] == False:
                    return d
                
                return {"status":True}
            else:
                return {"status":False, "error":"You are not logged in"}
        except Exception as e:
            return {"status":False, "error":str(e)}
    
@app.route('/add_admin_wallet', methods=['GET', 'POST']) 
def add_admin_wallet(): 
    if request.method == "GET":
        if "username" in session:
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    else:
        try:
            if "username" in session and "UUID" not in session:
                data = json.loads(request.get_data())
                price = data.get("price")
                admin_id = data.get("admin_id")
                
                db = Database()
                d = db.add_admin_wallet(int(admin_id), int(price))
                if d["status"] == False:
                    return d
                
                return {"status":True}
            else:
                return {"status":False, "error":"You are not logged in"}
        except Exception as e:
            return {"status":False, "error":str(e)}
    
@app.route('/set_server', methods=['GET', 'POST']) 
def set_server(): 
    if request.method == "GET":
        if "username" in session:
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    else:
        try:
            if "username" in session and "UUID" not in session:
                data = json.loads(request.get_data())
                url = data.get("url")
                username = data.get("username")
                password = data.get("password")
                
                sn = SanaeiAPI(username, password, url)
                da = sn.login()
                if (da["status"]):
                    db = Database()
                    d = db.set_servers(url, username, password)
                    if d["status"] == False:
                        return d
                    
                    return {"status":True}
                else:
                    return da
            else:
                return {"status":False, "error":"You are not logged in"}
        except Exception as e:
            return {"status":False, "error":str(e)}
        
@app.route('/get_config', methods=['GET', 'POST']) 
def get_config(): 
    if request.method == "GET":
        if "username" in session:
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    else:
        try:
            if "username" in session:
                data = json.loads(request.get_data())
                config_id = data.get("config_id")
                inbound_id = data.get("inbound_id")
                username = data.get("username")
                
                db = Database()
                server = db.get_servers()["data"][0]
                sn = SanaeiAPI(server["username"], server["password"], server["url"])
                url = sn.get_config(inbound_id, config_id, username)
                sn.create_qrcode(config_id, url)
                return {"status":True, "data":{"config_url":url}}
            else:
                return {"status":False, "error":"You are not logged in"}
        except Exception as e:
            return {"status":False, "error":str(e)}
        
        
@app.route('/logout') 
def logout(): 
    session.clear()
    return redirect(url_for("index"))
        
@app.route('/download_backup') 
def download_backup(): 
    try:
        if "username" in session and "UUID" not in session:
            with zipfile.ZipFile(os.path.join("backup.zip"), 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipdir(os.path.join("static"), zipf)
                zipf.setpassword(b"OminiCorp.com")
            return send_file(os.path.join("backup.zip"), as_attachment=True)
        else:
            return redirect(url_for("index"))
    except Exception as e:
        return render_template("error.html", error=str(e))

@app.route('/upload_backup', methods=['GET', 'POST']) 
def upload_backup(): 
    if request.method == "GET":
        if "username" in session:
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    else:
        try:
            if "username" in session and "UUID" not in session:
                if 'file' not in request.files:
                    return {"status": False, "error": "No file part"}
                file = request.files['file']
                if file.filename == '':
                    return {"status": False, "error": "No selected file"}
                file_path = os.path.join("restor.zip")
                file.save(file_path)
                with ZipFile(file_path, 'r') as zip:
                    zip.extractall(os.path.join("."))
                return {"status":True}
            else:
                return {"status":False, "error":"You are logged in"}
        except Exception as e:
            return {"status":False, "error":str(e)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run GODPanel server")
    parser.add_argument("--port", type=int, help="Port to run the server on")
    args = parser.parse_args()

    # اولویت: فلگ → متغیر محیطی → مقدار پیش‌فرض
    port = args.port or int(os.environ.get("PORT", 5050))
    app.run(debug=True, host="0.0.0.0", port=port)
