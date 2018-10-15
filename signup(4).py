
import os
from pymongo import MongoClient
from flask import *
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
connection = MongoClient()
db =connection['yrisc']

@app.route('/register',methods=['POST'])
@cross_origin()
def sign_up():
    coll = db.users
    name = request.json["name"]
    password = request.json["password"]
    email = request.json["email"]
    mobile = request.json["mobile"]
    emp_id = request.json["emp_id"]
    if name in  coll.distinct("name"):
        return "user exist"
    elif email in coll.distinct("email"):
        return "email exist"
    elif mobile in coll.distinct("mobile"):
        return "number already exist check"
    elif emp_id in coll.distinct("emp_id"):
        return "emp_id already exist"
    else:
        coll.insert({"name": request.json["name"],
                         "password": request.json["password"],
                         "email": request.json["email"],
                         "mobile": request.json["mobile"],
                         "emp_id": request.json["emp_id"]})
        return jsonify({"result": "sucessfully registered"})


@app.route("/login",methods=['POST'])
@cross_origin()
def login():
    coll = db.users
    name = request.json["name"]
    password = request.json["password"]
    a = (coll.find_one({"name": name}))
    if password == a["password"]:
        return jsonify({"result": "sucessfully login"})
    else :
        return jsonify({"result": "unsucessfully login"})

@app.route("/contacts",methods=['POST'])
@cross_origin()
def contacts():
    master = []
    cont = db.contacts
    appname = request.json["app"]
    con = cont.find_one({"app": appname})
    if con:
        for i in con["usercontact"]:
            if i["status"] == True:
                master.append(i)
        if len(master) > 1:
            return jsonify({"result":master})
        else:
            master = str(master).strip("[").strip("]")
            return jsonify({"result": master})
    else:
        return jsonify({"result": "invalid app name"})


@app.route("/privileges", methods=['POST'])
@cross_origin()
def privileges():
    data=db.user_info
    data1=db.infra_info
    name  = request.json["name"]
    main_list = {}
    for users in data.find():
        if name in users["name"] and users["userStatus"] == True:
            main_list["username"] = users["name"]
            main_list["privileges"] = []
            for user_apps in users["privileges"]:
                if user_apps["appStatus"] == True:
                    main_list_privileges = {}
                    main_list_privileges["application"] = user_apps["application"]
                    main_list_privileges["applicationData"] = {}
                    cmnd_env = user_apps["applicationData"]
                    if cmnd_env['envStatus']==True:
                        main_list_privileges["applicationData"]["env"] = []
                        for envs in cmnd_env['env']:
                            if envs["status"] == True:
                                env_dict = {}
                                env_dict["envname"]=envs["envname"]
                                for apps in data1.find():
                                    if apps["app"] == main_list_privileges["application"] and apps["appStatus"] == True:
                                        for environ in apps["envdata"]:
                                            if envs["envname"] == environ["env"] and environ["envStatus"] == True:
                                                env_dict["serversdata"] = []
                                                for servers in environ["serversdata"]:
                                                    if servers["status"] == True:
                                                        server_dict = {}
                                                        server_dict["servername"] = servers["servername"]
                                                        server_dict["serverip"] = servers["serverip"]
                                                        server_dict["server_username"] = servers["server_username"]
                                                        env_dict["serversdata"].append(server_dict)
                            main_list_privileges["applicationData"]["env"].append(env_dict)
                    if cmnd_env["cmdStatus"] == True:
                        main_list_privileges["applicationData"]["cmd"] = []
                        for cmnds in cmnd_env['cmd']:
                            if cmnds["status"] == True:
                                main_list_privileges["applicationData"]["cmd"].append(cmnds["cmdname"])

                main_list["privileges"].append(main_list_privileges)

    return jsonify({"result" :main_list})



if __name__ == '__main__':
    app.debug = True
    # Host = os.environ.get('IP', '0.0.0.0')
    # Port = int(os.environ.get('PORT', 8085))
    # app.run(host=Host, port=Port)

    app.run()
