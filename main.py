from flask import Flask ,session, render_template,request,send_file
from flask_restx import Resource, Api, reqparse
from flask_cors import  CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask_mail import Mail, Message
import jwt, os, random
from dotenv import load_dotenv
import subprocess
import pymysql
pymysql.install_as_MySQLdb()
load_dotenv()




app = Flask(__name__)
api = Api(app,title=os.environ.get("APP_NAME"))
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
mail = Mail(app)
db = SQLAlchemy(app)


class Users(db.Model):
    id       = db.Column(db.Integer(), primary_key=True, nullable=False)
    fullname     = db.Column(db.String(30), nullable=False)
    email    = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    address  = db.Column(db.String(255), nullable=True)
    no_hp = db.Column(db.String(15), nullable=True)
    is_verify = db.Column(db.String(20),nullable=False)

#parserRegister
regParser = reqparse.RequestParser()
regParser.add_argument('fullname', type=str, help='fullname', location='json', required=True)
regParser.add_argument('email', type=str, help='Email', location='json', required=True)
regParser.add_argument('password', type=str, help='Password', location='json', required=True)
regParser.add_argument('confirm_password', type=str, help='Confirm Password', location='json', required=True)

@api.route('/register')
class Registration(Resource):
    @api.expect(regParser)
    def post(self):
        # BEGIN: Get request parameters.
        args        = regParser.parse_args()
        fullname   = args['fullname']
        email       = args['email']
        password    = args['password']
        password2  = args['confirm_password']
        is_verify = 'not verify'

        # cek confirm password
        if password != password2:
            return {
                'messege': 'Password does not match',
                'code' : 400
            }, 400

        #cek email sudah terdaftar
        user = db.session.execute(db.select(Users).filter_by(email=email)).first()
        if user:
            return {'message': 'This email address has been used!'}
        user          = Users()
        user.fullname    = fullname
        user.email    = email
        user.password = generate_password_hash(password)
        user.is_verify = is_verify
        db.session.add(user)
        msg = Message(subject='Email Verification',sender=os.environ.get("MAIL_USERNAME"),recipients=[user.email])
        otp =  random.randrange(10000,99999)
        session['otpsession'] = str(otp)
        session['email'] = user.email
        msg.html=render_template(
        'emailotp.html', otp=otp)
        mail.send(msg)
        db.session.commit()
        return {'message': 'Register successfully, Please check Your email to verification', 'code' : 201}, 201


otpparser = reqparse.RequestParser()
otpparser.add_argument('otp', type=str, help='otp', location='json', required=True)
@api.route('/verify_email')
class VerifyEmail(Resource):
    @api.expect(otpparser)
    def post(self):
        args = otpparser.parse_args()
        otp = args['otp']
        if 'otpsession' in session:
            s= session['otpsession']
            if otp == s:
                email = session['email']
                user = Users.query.filter_by(email=email).first()
                user.is_verify = 'verified'
                db.session.commit()
                session.pop('otpsession',None)
                return {'message' : 'Your email has ben verified, Login Now', 'code' : 200},200
            else:
                return {'message' : 'Wrong Otp Code', 'code': 401},401
        else:
            return {'message' : 'Wrong Otp Code', 'code': 401},401




logParser = reqparse.RequestParser()
logParser.add_argument('email', type=str, help='email', location='json', required=True)
logParser.add_argument('password', type=str, help='password', location='json', required=True)

@api.route('/login')
class LogIn(Resource):
    @api.expect(logParser)
    def post(self):
        args        = logParser.parse_args()
        email       = args['email']
        password    = args['password']
        # cek jika kolom email dan password tidak terisi
        if not email or not password:
            return {
                'message': 'Please fill your email and password!',
                'code' : 400
            }, 400
        #cek email sudah ada
        user = db.session.execute(
            db.select(Users).filter_by(email=email)).first()
        if not user:
            return {
                'message': 'Wrong email or password',
                'code' : 400
            }, 400
        else:
            user = user[0]
        #cek password
        if check_password_hash(user.password, password):
            if user.is_verify == 'verified':
                token= jwt.encode({
                        "user_id":user.id,
                        "user_fullname":user.fullname,
                        "user_email": user.email,
                        "user_password": user.password,
                        "exp": datetime.utcnow() + timedelta(days= 1)
                },app.config['SECRET_KEY'],algorithm="HS256")
                return {'message' : 'Login successfully',
                        'code' : 200,
                        'token' : token
                        },200
            else:
                return {
                    'message' : 'Email has not been verified',
                    'code': 401
                    },401
        else:
            return {
                'message': 'Wrong email or password',
                'code' : 400
            }, 400

def dectoken(jwtToken):
    decode_token = jwt.decode(
               jwtToken,
               app.config['SECRET_KEY'],
               algorithms = ['HS256'],
            )
    return decode_token

# auth parser
authParser = reqparse.RequestParser()
authParser.add_argument('Authorization', type=str, help='Authorization', location='headers', required=True)

#edituserParser
editParser = reqparse.RequestParser()
editParser.add_argument('fullname', type=str, help='fullname', location='json', required=True)
editParser.add_argument('address', type=str, help='address', location='json', )
editParser.add_argument('no_hp', type=str, help='no_hp', location='json',)

@api.route('/user')
class User(Resource):
       #view user detail
       @api.expect(authParser)
       def get(self):
        args = authParser.parse_args()
        bearerAuth  = args['Authorization']
        try:
            jwtToken    = bearerAuth[7:]
            token = dectoken(jwtToken)
            user =  db.session.execute(db.select(Users).filter_by(id=token['user_id'])).first()
            user = user[0]
            data = {
                'name' : user.fullname,
                'address' : user.address,
                'no_hp' : user.no_hp,
                'email' : user.email,
            }
        except:
            return {
                'message' : 'Unauthorized! Token is invalid! Please, Sign in!','code': 401
            }, 401

        return data, 200

       #edit user
       @api.expect(authParser,editParser)
       def put(self):
        argss = authParser.parse_args()
        args = editParser.parse_args()
        bearerAuth  = argss['Authorization']
        fullname = args['fullname']
        address = args['address']
        no_hp = args['no_hp']

        try:
            jwtToken    = bearerAuth[7:]
            token = dectoken(jwtToken)
            user = Users.query.filter_by(id=token.get('user_id')).first()
            user.fullname = fullname
            user.address = address
            user.no_hp = no_hp
            db.session.commit()
        except:
            return {
                'message' : 'Unauthorized! Token is invalid! Please, Sign in!','code': 401
            }, 401
        return {
            'message' : 'User successfully updated',
            'code' : 200,

            }, 200

#editpasswordParser
editPasswordParser =  reqparse.RequestParser()
editPasswordParser.add_argument('current_password', type=str, help='current_password',location='json', required=True)
editPasswordParser.add_argument('new_password', type=str, help='new_password',location='json', required=True)
@api.route('/password')
class Password(Resource):
    @api.expect(authParser,editPasswordParser)
    def put(self):
        args = editPasswordParser.parse_args()
        argss = authParser.parse_args()
        bearerAuth  = argss['Authorization']
        oldpassword = args['current_password']
        newpassword = args['new_password']
        try:
            jwtToken    = bearerAuth[7:]
            token = dectoken(jwtToken)
            user = Users.query.filter_by(id=token.get('user_id')).first()
            if check_password_hash(user.password, oldpassword):
                user.password = generate_password_hash(newpassword)
                db.session.commit()
            else:
                return {'message' : 'Old password is wrong', 'code' : 400},400
        except:
            return {
                'message' : 'Unauthorized! Token is invalid! Please, Sign in!', 'code': 401
            }, 401
        return {'message' : 'Password successfully updated'}, 200


#parsersendemail
sendforgotpasswdparser=  reqparse.RequestParser()
sendforgotpasswdparser.add_argument('email', type=str, help='email',location='json', required=True)

resetpasswordparser=  reqparse.RequestParser()
resetpasswordparser.add_argument('password', type=str, help='password',location='json', required=True)
resetpasswordparser.add_argument('re_password', type=str, help='re_password',location='json', required=True)
resetpasswordparser.add_argument('token', type=str, help='token',location='args', required=True)


@api.route('/resetpassword')
class sendforgotpassword(Resource):
    @api.expect(sendforgotpasswdparser)
    def post(self):
        args = sendforgotpasswdparser.parse_args()
        email = args['email']
        user = Users.query.filter_by(email=email).first()
        if user is None:
            return {'message': 'Your Email Not Register', 'code' : 400},400
        else:
            token = jwt.encode({
                        "email": email,
                        "exp": datetime.utcnow() + timedelta(minutes= 10)
                },app.config['SECRET_KEY'],algorithm="HS256")
            baseurl = request.base_url
            url = baseurl + '?token=' + str(token)
            msg = Message(subject='Reset Password ',sender=os.environ.get("MAIL_USERNAME"),recipients=[email])
            msg.html=render_template(
            'emailforgotpassword.html', url=url)
            mail.send(msg)
            return {'message' : 'Check your email to reset password','code': 200},200
    @api.expect(resetpasswordparser)
    def put(self):
        args = resetpasswordparser.parse_args()
        password = args['password']
        re_password = args['re_password']
        token = args['token']
        token = dectoken(token)
        user = Users.query.filter_by(email=token.get('email')).first()
        if password != re_password:
            return {
                'message': 'Password does not match', 'code' : 400
            }, 400
        else:
            user.password = generate_password_hash(password)
            db.session.commit()
            return {'message' : 'Success Change Password'}, 200



ALLOWED_EXTENSIONS = {'3gp', 'mkv', 'avi', 'mp4'}
def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

detectParser = api.parser()
# detectParser.add_argument('video', location='files', type=FileStorage, required=True)
detectParser.add_argument('video', location='files', type=FileStorage)
@api.route('/detect')
class Detect(Resource):
    @api.expect(detectParser)
    def post(self):
        args = detectParser.parse_args()
        video = args['video']
        if video and allowed_file(video.filename):
            filename = secure_filename(video.filename)
            video.save(os.path.join("./videoTemp", filename))
            subprocess.run(['python', 'detect.py', '--source', f'./videoTemp/{filename}', '--weights', 'best.pt','--conf', '0.5', '--name', f'{filename}'])
            os.remove(f'./videoTemp/{filename}')
            print('success remove')
            return send_file(os.path.join(f"./runs/detect/{filename}", filename), mimetype='video/mp4', as_attachment=True, download_name=filename)
        else:
            return {'message' : 'invalid file extension'},400

@app.route("/realtime")
def hello_world():
    return render_template('index.html')

@app.route("/opencam", methods=['GET'])
def opencam():
    print("waittt opencammm")
    subprocess.run(['python', 'detect.py', '--source', '0', '--weights', 'best.pt','--conf', '0.5'])
    return "done"


@app.route('/resetpassword', methods=["GET"] )
def ResetPassword():
    token =request.args.get('token')
    if token is None:
        return render_template('notfound.html')
    else:
        return  render_template('formresetpassword.html')



if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')
     app.run(host='0.0.0.0', port=5000, debug=True)
