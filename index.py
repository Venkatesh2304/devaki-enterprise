from fileinput import filename
import hashlib
from datetime import timedelta
from urllib import response
# Flask, request, jsonify , send_file , make_response , Response , send_from_directory
from flask import *
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
from pymongo import MongoClient
from hul import *
import ewaysite
from flask_cors import CORS
# date parser
def dateParser(date): return datetime.strptime(date, "%Y-%m-%d")

def SendExcel(df,download_name):
     output = BytesIO()
     with pd.ExcelWriter(output, engine='xlsxwriter') as writer : 
         df.to_excel(writer,index=False)
         writer.save()
     output.seek(0)
     return  send_file( output ,  mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" , 
                    download_name= download_name )


app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1/:5000",
     "http://127.0.0.1:5501"], supports_credentials=True)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'abcdef'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=15)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

# your connection string
client = MongoClient(
    "mongodb+srv://venkatesh2004:venkatesh2004@cluster0.9x1ccpv.mongodb.net/?retryWrites=true&w=majority")
db = client["demo"]
users = db["users"]
configs = db["config"]

# @app.route("/signup", methods=["POST"])
# def register():
#     new_user = request.get_json() # store the json body request
#     new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest() # encrpt password
#     doc = users.find_one({"username": new_user["username"]}) # check if user exist
#     if not doc:
#         users.insert_one(new_user)
#         return jsonify({'msg': 'User created successfully'}), 201
#     else:
#         return jsonify({'msg': 'Username already exists'}), 409




@app.route("/login", methods=["GET"])
def loginpage():
    return app.send_static_file("login.html")

@app.route("/login", methods=["POST"])
def login():
    login_details = request.get_json()  # store the json body request
    # search for user in database
    user_from_db = users.find_one({'username': login_details['username']})
    if user_from_db:
        encrpted_password = hashlib.sha256(
            login_details['password'].encode("utf-8")).hexdigest()
        if encrpted_password == user_from_db['password']:
            access_token = create_access_token(
                identity=user_from_db["username"])  # create jwt token
            response = jsonify({"status" : True , "redirect" : "/"})
            set_access_cookies(response, access_token)
            return response
        else:
            return jsonify({"status": False ,"err": "Wrong Password"}), 401
    else:
        login_details["password"] = hashlib.sha256(
            login_details['password'].encode("utf-8")).hexdigest()
        users.insert_one(login_details)
        response = jsonify({"status" : True , "redirect" : "/update"})
        access_token = create_access_token(
                identity= login_details["username"]) 
        set_access_cookies(response, access_token)
        return response


@jwt.unauthorized_loader
def custom_unauthorized_response(_err):
    return redirect(url_for('login'))

#Web page rendering :: start 
@app.route("/", methods=["GET"])
@jwt_required()
def MainPage():
    return app.send_static_file("index.html")

@app.route("/update", methods=["GET"])
@jwt_required()
def UpdatePage():
    return app.send_static_file("update.html")
#Web page Rendering :: end 

#Update Stuff ::: start 
@app.route("/preload", methods=["GET"])
@jwt_required()
def Preload():
    user = get_jwt_identity()
    data = dict(users.find_one({"username" : user}))
    required = ["ikea_user" , "ikea_pwd" , "dbName", "baseUrl" , "eway_user" , "eway_password" , 
                "einv_user" , "einv_password" ]
    data = { i : j for i , j in data.items() if i in required }
    return jsonify(data)

@app.route("/preDownload/<type>", methods=["GET"])
@jwt_required()
def PreDownload(type):
    user = get_jwt_identity()
    data = configs.find_one({"username" : user})
    if type == "vehicle" : 
        temp = pd.DataFrame([[i,j] for i , j in data["vehicles"].items()] , columns = ["Name","Vehicle No"])
        return SendExcel( temp , "vehicles.xlsx")
        

@app.route("/verify", methods=["POST"])
@jwt_required()
def verify():
    user = get_jwt_identity()
    data = request.get_json()
    [Type, data] = data
    if Type == "ikea":
        users.update_one({"username": user}, {"$set": data }, upsert=True)
        status , err  = ikea(user,users,isReload=False).login() 
        return jsonify({ "status" : status , "err" : err }) , 200 

    if Type == "eway" or Type == "einvoice" :
        users.update_one({"username": user}, {"$set": data }, upsert=True)
        return jsonify({ "status" : True  , "err" : "Success" }) , 200 

@app.route("/postUpdate", methods=["POST"])
@jwt_required()
def postUpdate():
    user = get_jwt_identity()
    data = dict(request.form)
    users.update_one({"username" : user }, { "$set" : data }, upsert = True ) 
    for  fname , file in dict(request.files).items() : 
        if file : 
           df = pd.read_excel(file)  
           if fname == "vehicle" : 
              update = { "vehicles" : { i : j  for [i,j] in df.values.tolist() }}
              configs.update_one({ "username" : user} , { "$set" : update } , upsert =True )
              return redirect("/")
            #return jsonify({ "status" : True , "err" : "Success"})
    
#Update Ends :::



#Eway and Einvoice :: Start 

#Preloaders :: getbeats && getVehicle 
@app.route("/getbeats", methods=["POST"])
@jwt_required()
def getBeats():
    data = request.get_json()
    user = get_jwt_identity()
    session = ikea(user, users)
    beats = session.getBeats(dateParser(
        data["fromDate"]), dateParser(data["toDate"]))
    return beats

@app.route("/getvehicle", methods=["GET"])
@jwt_required()
def getVehicle():
    user = get_jwt_identity()
    vehicles = configs.find_one({"username": user})
    if vehicles:
        return vehicles["vehicles"]
    else:
        return jsonify({"err": "No vehciles exists"})
#Preloaders :: End 

#Login For Eway and Einvoice
@app.route("/ewayLogin", methods=["POST", "GET"])
@jwt_required()
def ewayLogin():
    user = get_jwt_identity()
    types = request.args.get(
        "types") if request.method == "GET" else request.get_json()["types"]
    maps = {"einvoice": einvsite.Einvoice, "eway": ewaysite.Eway}
    esession = maps[types]()
    if request.method == "POST":
        data = request.get_json()
        data.update(json.loads(request.cookies.get("data")))
        return jsonify(esession.login(user, users, data))
    else:
        img, data = esession.getCaptcha()
        response = make_response(send_file(img, mimetype='image/aspx'))
        response.set_cookie("data", json.dumps(data))
        return response

#Generate Eway or Einvoice , return the json ( which contains the excel )
@app.route("/eGenerate", methods=["POST"])
@jwt_required()
def generateEway():
    user = get_jwt_identity()
    data = request.get_json()
    data["fromDate"],data["toDate"] = dateParser(data["fromDate"]),dateParser(data["toDate"])
    x = ikea(user,users).EGenerate(**data)
    return x 
    #if type(x) == dict :
    #    return jsonify(x)
    #return send_file( x ,  mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" , 
    #                       download_name= data["types"] +  ".xlsx" )


@app.route("/outstanding", methods=["POST"])
@jwt_required()
def Outstanding():
    user = get_jwt_identity()
    data = request.get_json()
    date, days = dateParser(data["date"]), data["days"]
    return ikea(user,users).outstanding(date , days)


@app.route("/creditlock", methods=["GET"])
@jwt_required()
def CreditLock():
    user = get_jwt_identity()
    return ikea(user, users).creditlock(configs)


if __name__ == '__main__':
    app.run(debug=True)
