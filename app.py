from flask import *
from flask import jsonify
from gtts import gTTS
from googletrans import Translator, LANGUAGES
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import speech_recognition as sr
from datetime import datetime

language_codes = list(LANGUAGES.keys())
language_names = list(LANGUAGES.values())

app=Flask(__name__,static_folder='static/')
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///informaiton.db'
app.config["SQLALCHEMY_TRACK_MODIFICATION"]=False
db = SQLAlchemy(app)
class login(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(200),nullable=False)
    password=db.Column(db.String(8),nullable=False)
    date=db.Column(db.DateTime,default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.email} - {self.password}"
    

@app.route('/', methods=['GET','POST'])
def loge():
    if request.method=='POST':
        d={}
        emails = [i.email for i in login.query.with_entities(login.email).all()]
        password = [i.password for i in login.query.with_entities(login.password).all()]
        for i in range(len(emails)):
                d[emails[i]]= password[i]
        global email
        email=request.form.get('email')
        password=request.form.get('password')

        if email not in d.keys():
            message2="User dosen't Exist "
            return render_template('login2.html',message2=message2)

        if email in d.keys():
            if d[email] == password:
                return redirect(url_for("home"))
            else:
                message="Wrong Password"
                return render_template("login2.html",message=message)
    return render_template("login2.html")

@app.route('/signup', methods=['GET','POST'])
def loge2():
    if request.method=='POST':
        emails= [i.email for i in login.query.with_entities(login.email).all()] 
        email=request.form.get('email')
        if email in emails:
            error="USER ALREADY EXISTS"
            return render_template('login.html',error=error)
        else:
            email=request.form.get('email')
            password=request.form.get('password')
            lgn = login(email=email,password=password,date=datetime.utcnow())
            db.session.add(lgn)
            db.session.commit()
        
    return render_template("login.html")

@app.route("/home",methods=['GET', 'POST'])
def home():
    try:
        return render_template('home.html',email=email)
    except:
        return render_template('home.html')
    
@app.route("/data")
def data():

    info = login.query.all()
    return render_template("data.html",info = info)

@app.route("/delete/<int:sno>")
def delete(sno):
    log = login.query.filter_by(sno=sno).first()
    db.session.delete(log)  
    db.session.commit()
    return redirect('/home')

@app.route('/convert',methods=['POST'])
def convert():
    if request.method=='POST':
        data=request.form['data']
        if len(data)==0:
            return render_template('empity.html')
        else:
            myfile=gTTS(text=data,lang='en',slow=False)
            myfile.save('./media/output.mp3')

    return render_template('download.html')

@app.route('/download',methods=['POST'])
def download():
    if request.method=='POST':
        return send_file('./media/output.mp3',as_attachment=True)

@app.route('/trans')
def index():
    return render_template('trans.html', source_languages=zip(language_codes, language_names), target_languages=zip(language_codes, language_names))

@app.route('/translate', methods=['POST'])
def translate_text():
    text_to_translate = request.form.get('text')
    source_language = request.form.get('source_language')
    target_language = request.form.get('target_language')
    if not text_to_translate or not source_language or not target_language:
        return jsonify({'translation': 'Please provide valid input.'})

    translator = Translator()
    try:
        translation = translator.translate(text_to_translate, src=source_language, dest=target_language).text
    except Exception as e:
        print(f"Translation error: {e}")
        translation = "Translation failed. Please try again later."

    return jsonify({'translation': translation})

@app.route('/pronounce', methods=['POST'])
def pronounce_text():
    text = request.json.get('text')
    if text:
        return jsonify({'message': 'Text pronounced successfully!'})
    else:
        return jsonify({'message': 'Text not provided for pronunciation.'})
    
@app.route("/speech", methods=["GET", "POST"])
def speech():
    transcript = ""
    if request.method == "POST":
        print("FORM DATA RECEIVED")

        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            error='UPLODE AN AUDIO FILE FIRST :/ '
            return render_template('speech.html', error=error)
        try:
            if file:
                recognizer = sr.Recognizer()
                audioFile = sr.AudioFile(file)
                with audioFile as source:
                    data = recognizer.record(source)
                transcript = recognizer.recognize_google(data, key=None)
        except:
            error2="NOTE THE ABOVE MENTIONED FILE TYPE :/ "
            return render_template('speech.html',error2=error2)

    return render_template('speech.html', transcript=transcript)

@app.route('/logout')
def out():
    return render_template('login2.html')

@app.route('/about', methods=["GET","POST"])
def about():
    if request.method=='POST':
        email1 = login.query.all()
        return render_template('about.html',email1=email1)
    return render_template('about.html')


if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)