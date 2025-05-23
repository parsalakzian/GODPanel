import base64
import math
import uuid
import requests
import json
import os
import time
import qrcode
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont
import urllib
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate
from reportlab.lib import colors

class SanaeiAPI():
    def __init__(self, username, password, url:str):
        self.username = username
        self.password = password
        self.url = url
        self.server = url.replace("http://","").replace("https://", "").split("/")[0].split(":")[0]
        self.pathes = {
            'login': '/login',
            'inbounds': '/panel/api/inbounds/list/',
            'inbound':'/panel/api/inbounds/get/{}',
            'add_client':'/panel/api/inbounds/addClient/',
            'update_client':'/panel/api/inbounds/updateClient/{}',
            'reset':'/panel/api/inbounds/{}/resetClientTraffic/{}',
            'client_traffic':'/panel/api/inbounds/getClientTraffics/{}',
            'onlines':'/panel/api/inbounds/onlines/'
        }
        
    def custom_uuid(self, admin_id, width=8):
      prefix = str(admin_id).zfill(width)[:width]
      u = str(uuid.uuid4())
      parts = u.split('-')
      parts[0] = prefix
      return '-'.join(parts)
        
    def saveCookie(self, Cookie):
        with open(os.path.join('cookie.json'), 'w') as f:
            f.write(json.dumps(Cookie))
            
    def loadCookie(self):
        if os.path.exists('cookie.json'):
            with open(os.path.join('cookie.json'), 'r') as f:
                return json.loads(f.read())
        else:
            self.login()
            return self.loadCookie()
        
    def login(self):
        try:
            data = requests.post(
                url=self.url + self.pathes["login"],
                data={
                    'username': self.username,
                    'password': self.password
                }
            )
            if data.json():
                if data.json()["success"]:
                    self.saveCookie({
                        data.headers.get("Set-Cookie").split("=")[0]: data.headers.get("Set-Cookie").split(";")[0].replace("3x-ui=", "")
                    })
                    return {"status":True}
                else:
                    return {"status":False, "error":data.json()["msg"]}
            else:
                return {"status":False}
        except Exception as error:
            return {"status":False, "error":str(error)}
        
    def get_inbounds(self):
        data = requests.get(url=self.url + self.pathes["inbounds"], cookies=self.loadCookie())
        if data.json():
            inbounds = []
            for inbound in data.json()["obj"]:
                inbounds.append({
                    "id": inbound["id"],
                    "remark": inbound["remark"],
                })
            return {"status":True, "data":inbounds}
        else:
            self.login()
            return self.get_inbounds()
        
    def get_inbound(self, inbound_id):
        data = requests.get(url=self.url + self.pathes["inbound"].format(inbound_id), cookies=self.loadCookie())
        if data.json():
            if data.json()["success"]:
                return {"status":True, "data":data.json()["obj"]}
            else:
                return {"status":False, "error":data.json()["msg"]}
        else:
            self.login()
            return self.get_inbound(inbound_id)
        
    def get_client_traffic(self, username):
        data = requests.get(url=self.url + self.pathes["client_traffic"].format(username), cookies=self.loadCookie())
        if data.json():
            if data.json()["success"]:
                return {"status":True, "data":int(data.json()["obj"]["total"] - (data.json()["obj"]["up"] + data.json()["obj"]["down"])), }
            else:
                return {"status":False, "error":data.json()["msg"]}
        else:
            self.login()
            return self.get_client_traffic()
        
    def add_client(self, inbound_id, username, admin_id, traffic= 64424509440, doration=-2592000000):
        uid = str(self.custom_uuid(admin_id))
        settings = "{\"clients\": [{\"id\": \""+uid+"\",\"flow\": \"\",\"email\": \""+username+"\",\"limitIp\": 0,\"totalGB\": "+str(traffic)+",\"expiryTime\": "+str(doration)+",\"enable\": true,\"tgId\": \"\",\"subId\": \"\",\"reset\": 0}]}"
        data = requests.post(
            url=self.url + self.pathes["add_client"],
            cookies=self.loadCookie(),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            data= json.dumps({
                "id":inbound_id,
                "settings": settings
            })
        )
        if data.json():
            if data.json()["success"]:
                return {"status":True, "id":uid, "username":username}
            else:
                return {"status":False, "error":data.json()["msg"]}
        else:
            self.login()
            return self.add_client(inbound_id, username, traffic, doration)
        
    def update_client(self, inbound_id, uid, username, traffic= 64424509440, doration= int(time.time())*1000 + 2600000000):
        settings = "{\"clients\": [{\"id\": \""+uid+"\",\"flow\": \"\",\"email\": \""+username+"\",\"limitIp\": 0,\"totalGB\": "+str(traffic)+",\"expiryTime\": "+str(doration)+",\"enable\": true,\"tgId\": \"\",\"subId\": \"\",\"reset\": 0}]}"
        data = requests.post(
            url=self.url + self.pathes["update_client"].format(uid),
            cookies=self.loadCookie(),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            data= json.dumps({
                "id":inbound_id,
                "settings": settings
            })
        )
        if data.json():
            if data.json()["success"]:
                return {"status":True, "id":uid, "username":username}
            else:
                return {"status":False, "error":data.json()["msg"]}
        else:
            self.login()
            return self.update_client(inbound_id, uid, username, traffic, doration)
        
    def reset_client_traffic(self, inbound_id, username):
        data = requests.post(
            url=self.url + self.pathes["reset"].format(inbound_id, username),
            cookies=self.loadCookie(),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
        )
        if data.json():
            if data.json()["success"]:
                return {"status":True, "username":username}
            else:
                return {"status":False, "error":data.json()["msg"]}
        else:
            self.login()
            return self.reset_client_traffic(inbound_id, username)
        
    def onlines(self):
        data = requests.post(
            url=self.url + self.pathes["onlines"],
            cookies=self.loadCookie(),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
        )
        if data.json():
            if data.json()["success"]:
                return {"status":True, "onlines":data.json()["obj"]}
            else:
                return {"status":False, "error":data.json()["msg"]}
        else:
            self.login()
            return self.onlines()
    
    def GetConfig(self, stream:str, uuid: str, email: str, port: str, protocol: str, serverName: str):
        # Your Remark
        inboundSetting = json.loads(stream)
    
        remark = f"New {email}"

        path = None
        host = "none"
        domainName = None
        serviceName = None
        headerType = None
        alpn = None
        kcpType = None
        grpcSecurity = None
        
    # Get Security 
        fingerPrint = ""
    
        tls = inboundSetting["security"]

        if  tls == "reality":
        
    
            fingerPrint = inboundSetting['realitySettings']['settings']['fingerprint']
            global publicKey 
            publicKey =  inboundSetting['realitySettings']['settings']['publicKey']
            global shortIds
            shortIds = inboundSetting['realitySettings']['shortIds'][0]
            global spiderX
            spiderX = inboundSetting['realitySettings']['settings']['spiderX']
            global sni
            sni = inboundSetting['realitySettings']['serverNames'][0]
    
        if tls == "tls":
            domainName = inboundSetting["tlsSettings"]["serverName"]
        elif tls == "xtls":
            domainName = inboundSetting["xtlsSettings"]["serverName"]
            alpn =  inboundSetting["tlsSettings"][0]["certificates"]["alpn"][0]
            global allowInsecure 

            allowInsecure = inboundSetting["tlsSettings"][0]["certificates"]["allowInsecure"]
    
    
        #    Get Net Type Setting
        netType = inboundSetting["network"]
        if netType == "grpc":
            serviceName = inboundSetting["grpcSettings"]["serviceName"]
            grpcSecurity = inboundSetting["security"]
        elif netType == "tcp":
            headerType = inboundSetting["tcpSettings"]["header"]["type"]
            if headerType != 'none':
                
                path = quote(inboundSetting["tcpSettings"]["header"]["request"]["path"][0], safe='') 
                try:
                    try:
                        
                        host = inboundSetting["tcpSettings"]["header"]["request"]["headers"]["host"][0]
                    except:
                        host = inboundSetting["tcpSettings"]["header"]["request"]["headers"]["Host"][0]
                except:  
                    host = ""       
                    
        elif netType == "ws":
        
            path = quote(inboundSetting["wsSettings"]["path"], safe='') 
            try:
                host = inboundSetting["wsSettings"]["headers"]["host"]
            except:
                host=""    
        elif netType == "kcp":
            kcpType = inboundSetting["kcpSettings"]["header"]["type"]
            kcpSeed = inboundSetting["kcpSettings"]["seed"]




        #  Get Protocol . Final Step 
        if protocol == "shadowsocks":
            setting = json.loads(stream['settings'])
            confFirst = f"{setting['method']}:{setting['password']}:{uuid}"
            Clients = ""
            decoded_bytes = base64.urlsafe_b64encode(confFirst )
            if tls == "tls":
                    conf += f"&security={tls}&fp={fingerPrint}&alpn={alpn}{'&allowInsecure=1' if allowInsecure ==True else'' }&sni={sni}"
            if netType == "tcp" : 
                return (
                    f"{protocol}://{decoded_bytes}@{serverName}:{port}?type={netType}"
                    + (
                        f"&headerType={headerType}&path={path if path != '' else '/'}&host={host}"
                        if headerType != "none"
                        else ""
                    )
                    + f"{conf}#{remark}"
                )


            elif netType == "ws" or netType == "httpupgrade" or netType == "splithttp" :
                return  f"{protocol}://{uuid}@{serverName}:{port}?type={netType}&path={path if path!='' else '/'}&host={host}{conf}#{remark}"
                            
            elif netType == "kcp":
                return  f"{protocol}://{decoded_bytes}@{serverName}:{port}?type={netType}&security={tls}&headerType={kcpType}&seed={kcpSeed}#{remark}"             
                
            if netType == "grpc":
                
                authority = inboundSetting['grpcSettings']['authority']
            
                conf  = f"&serviceName={serviceName}&authority={authority}" + conf
                

                return (
                    f"{protocol}://{uuid}@{serverName}:{port}?type={netType}"
                    + (
                        f"&headerType={headerType}&path={path if path != '' else '/'}&host={host}"
                        if headerType != "none"
                        else ""
                    )
                    + f"{conf}#{remark}"
                )



    
    
        if protocol == "trojan":
            conf = ""
            if tls == "reality":
                conf += f"&security={tls}&pbk={publicKey}&fp={fingerPrint}&sni={sni}&sid={shortIds}&spx={spiderX}"             
            if tls == "tls":
                conf += f"&security={tls}&fp={fingerPrint}&alpn={alpn}{'&allowInsecure=1' if allowInsecure ==True else'' }&sni={sni}"
            if netType == "tcp" : 
                return (
                    f"{protocol}://{uuid}@{serverName}:{port}?type={netType}"
                    + (
                        f"&headerType={headerType}&path={path if path != '' else '/'}&host={host}"
                        if headerType != "none"
                        else ""
                    )
                    + f"{conf}#{remark}"
                )


            elif netType == "ws" or netType == "httpupgrade" or netType == "splithttp" : return  f"{protocol}://{uuid}@{serverName}:{port}? type={netType}&path={path if path!='' else '/'}&host={host}{conf}#{remark}"
                        
            elif netType == "kcp": return  f"{protocol}://{uuid}@{serverName}:{port}?type={netType}&security={tls}&headerType={kcpType}&seed={kcpSeed}#{remark}"             
                
            if netType == "grpc":
                
                authority = inboundSetting['grpcSettings']['authority']
            
                conf  = f"&serviceName={serviceName}&authority={authority}" + conf
                

                return (
                    f"{protocol}://{uuid}@{serverName}:{port}?type={netType}"
                    + (
                        f"&headerType={headerType}&path={path if path != '' else '/'}&host={host}"
                        if headerType != "none"
                        else ""
                    )
                    + f"{conf}#{remark}"
                )

        elif protocol == "vless":
            conf = ""
            if netType == "tcp":

                if tls == "xtls":
                    conf += f"&security={tls}&flow=xtls-rprx-direct"
                if tls == "reality":
                    conf += f"&security={tls}&pbk={publicKey}&fp={fingerPrint}&sni={sni}&sid={shortIds}&spx={spiderX}"     
                if tls == "tls":
                    conf += f"&security={tls}&fp={fingerPrint}&alpn={alpn}{'&allowInsecure=1' if allowInsecure ==True else'' }&sni={sni}"
                if host =="none" :
                    host=""    
                newConfig = (
                    f"{protocol}://{uuid}@{serverName}:{port}?type={netType}"
                    + (
                        f"&headerType={headerType}&path={path if path != '' else '/'}&host={host}"
                        if headerType != "none"
                        else ""
                    )
                    + f"{conf}#{remark}"
                )

            elif netType == "ws":
                if tls == "tls":
                
                    conf += f"&security={tls}&fp={fingerPrint}&alpn={alpn}{'&allowInsecure=1' if allowInsecure == True else'' }&sni={sni}"

                newConfig = f"{protocol}://{uuid}@{serverName}:{port}?type={netType}&path={path if path!='' else '/'}&host={host}{conf}#{remark} "
            elif netType == "kcp":
                newConfig = f"{protocol}://{uuid}@{serverName}:{port}?type={netType}&security={tls}&headerType={kcpType}&seed={kcpSeed}#{remark}"
            elif netType == "grpc":
                
                authority = inboundSetting['grpcSettings']['authority']
            
                conf  = f"&serviceName={serviceName}&authority={authority}" + conf
                if tls == "xtls":
                    conf += "&flow=xtls-rprx-direct"
                if tls == "reality":
                    conf += f"&security={tls}&pbk={publicKey}&fp={fingerPrint}&sni={sni}&sid={shortIds}&spx={spiderX}"     
                if tls == "tls":
                    conf += f"&security={tls}&fp={fingerPrint}&alpn={alpn}{'&allowInsecure=1' if allowInsecure ==True else'' }&sni={sni}"
                newConfig = f"{protocol}://{uuid}@{serverName}:{port}?type={netType}&serviceName={serviceName}#{remark}"
        elif protocol == "vmess":
            vmessConf = {
                "v": "2",
                "ps": f"{remark}",
                "add": serverName,
                "port": int(port),
                "id": uuid,
                "aid": 0,
                "net": netType,
                "type": "none",
                "tls": "none",
                "path": "",
                "host":  ""

            }
        
    
            if headerType != None:
                vmessConf["type"] = headerType
            elif kcpType != None:
                vmessConf["type"] = kcpType
            else:
                vmessConf["type"] = "none"

            if host != None or host != "none":
                vmessConf["host"] = host
            if path == None or path == '':
                vmessConf["path"] = "/"
            else:
                vmessConf["path"] = path
            if  tls == "" or tls =="none":
                vmessConf["tls"] = "none"

            else:
                vmessConf["tls"] = tls
            if headerType == "http":
                vmessConf["path"] = "/"
                vmessConf["type"] = headerType
            if netType == "kcp":
                if kcpSeed != None or kcpSeed != "":
                    vmessConf["path"] = kcpSeed

            if netType == "grpc":
                vmessConf['type'] = grpcSecurity
                vmessConf['scy'] = 'auto'
            if netType == "httpupgrade" or netType == "splithttp":
                vmessConf['scy'] = 'auto'
            res = json.dumps(vmessConf)
            res =res[1:]

            res = "{\n"  +  res.replace("}","\n}")
            res = res.replace("," ,",\n ")
            sample_string_bytes = res.encode("ascii")
        
            base64_bytes = base64.b64encode(sample_string_bytes)
            base64_string = base64_bytes.decode("ascii")
            
            newConfig = f"vmess://{base64_string}"
        return newConfig
    
    def get_config(self, inbound_id, uid, username):
        data = self.get_inbound(inbound_id)
        if data["status"]:
            inbound = data["data"]
        else:
            return data["error"]
        return self.GetConfig(inbound["streamSettings"], uid, username, inbound["port"], inbound["protocol"], self.server)
    
    def download_font_if_needed(self, font_path):
        if not os.path.exists(font_path):
            print("دانلود فونت DejaVuSans.ttf ...")
            url = "https://github.com/prawnpdf/prawn/raw/refs/heads/master/data/fonts/DejaVuSans.ttf"
            urllib.request.urlretrieve(url, font_path)
            print("فونت دانلود شد.")

    def create_qrcode(self, uid, config, text="Your Text Here"):
        
        name = f"New {text}"
        # مسیر محلی برای ذخیره فونت
        font_path = os.path.join(os.getcwd(), "DejaVuSans.ttf")
    
        # دانلود فونت در صورت نیاز
        self.download_font_if_needed(font_path)
    
        # بارگذاری فونت با اندازه بزرگ
        font = ImageFont.truetype(font_path, size=90)
    
        # تولید QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
            border=4,
        )
        qr.add_data(config)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
        # محاسبه اندازه متن
        dummy_img = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
    
        # آماده‌سازی تصویر نهایی
        padding_x = 60
        padding_y = 60
        new_width = max(qr_img.width, text_width) + padding_x
        new_height = qr_img.height + text_height + padding_y
    
        final_img = Image.new("RGB", (new_width, new_height), "white")
        qr_x = (new_width - qr_img.width) // 2
        final_img.paste(qr_img, (qr_x, padding_y // 2))
    
        # رسم متن
        draw = ImageDraw.Draw(final_img)
        text_x = (new_width - text_width) // 2
        text_y = qr_img.height + padding_y // 2
        draw.text((text_x, text_y), name, font=font, fill="black")
    
        # ذخیره تصویر
        output_path = os.path.join("static", "qrcodes", f'{name}.png')
        final_img.save(output_path)
        return output_path
    
    def get_admin_clients(self, inbound_id, admin_id):
        data = self.get_inbound(inbound_id)
        if data["status"]:
            inbound = data["data"]
            settings = json.loads(inbound["settings"])
            if settings["clients"]:
                onlines = self.onlines()["onlines"] if self.onlines()["onlines"] != None else []
                online = 0
                expiryes = 0
                clients =  settings["clients"]
                prefix = str(admin_id).zfill(8)[:8]
                admin_clients = []
                for cl in clients:
                    if str(cl["id"]).startswith(prefix):
                        if cl["expiryTime"] > 0 and float(cl["expiryTime"] - int(time.time()) * 1000) > 0:
                            ext = math.ceil(float((cl["expiryTime"] - int(time.time()) * 1000)/1000/60/60/24))
                        elif cl["expiryTime"] == -2592000000:
                            ext = 30
                        else:
                            ext = 0
                        # print(ext)
                        traf = self.get_client_traffic(cl["email"])
                        traff = 0
                        if traf["status"]:
                            traff = traf["data"]
                        else:
                            return traf
                        
                        if cl["email"] in onlines:
                            online += 1
                        if ext == 0:
                            expiryes += 1
                            
                        admin_clients.append({
                            "id": cl["id"],
                            "username": cl["email"],
                            "inbound_id": inbound_id,
                            "status": "ON" if cl["email"] in onlines else "OFF",
                            "traffic": int(traff/1024/1024/1024),
                            "doration":ext,
                        })
                    
                return {"status":True, "data":{
                    "onlines":online,
                    "expiryes":expiryes,
                    "clients":admin_clients
                }}
            else:
                return {"status":True, "data":{
                    "onlines":[],
                    "expiryes":0,
                    "clients":0
                }}
        else:
            return {"status": False, "error":data["error"]}
        
    def generate_pdf(self, data:list, filename="wallet_report"):
        try:
            # Add header row
            header = ["EVENT", "DECREASE", "WALLET"]
            table_data = [header] + data
            
            # Set up PDF document
            doc = SimpleDocTemplate(
                os.path.join("static", "reports", filename + ".pdf"),
                pagesize=A4,
                rightMargin=30, leftMargin=30,
                topMargin=30, bottomMargin=30
            )
            
            # Create a Table
            table = Table(table_data, colWidths=[120, 120, 120, 120])

            # Style the table
            style = TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),

                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),

                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ])
            table.setStyle(style)

            # Build PDF
            elements = [table]
            doc.build(elements)

            return {"status": True, "data":{"file_path":os.path.join("static", "reports", filename + ".pdf")}}
        except Exception as e:
            return {"status": False, "error": str(e)}
        
                
# sn = SanaeiAPI("GOD", "Man.69.MyXras", "http://www.x8ss0.com:443/oxoxo")
# print(json.dumps(sn.update_client(8, "3ff0b0fe-15dd-11f0-a002-60dd8efd8828", "test"), indent=4))
# sn.create_qrcode("3ff0b0fe-15dd-11f0-a002-60dd8efd8828", sn.get_config(8, "3ff0b0fe-15dd-11f0-a002-60dd8efd8828", "test"))
# print(sn.get_admin_clients(6, 5))