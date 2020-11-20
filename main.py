from flask import Flask, render_template,request,session,redirect, flash
from flask_socketio import SocketIO,join_room
from flask_sqlalchemy import SQLAlchemy
import jwt,click
from werkzeug.security import check_password_hash,generate_password_hash



app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/flask_chat'
db = SQLAlchemy(app)
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    def __init__(self, **kw):
		   self.username = kw['username']
		   self.password =generate_password_hash(kw['password'])
    def __repr__(self):
        return '<Users {},{}>'.format(self.username, self.password)
	
class Chat(db.Model):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(120), db.ForeignKey('users.username'))
    msg = db.Column(db.Text)
    to = db.Column(db.String(120))
    you = db.Column(db.String(120))
    def __repr__(self):
        return '<Users {},{},{},{}>'.format(self.username, self.msg, self.to, self.you)



@app.route('/register', methods=['GET', 'POST'])
def Create():
	if 'name' in session: 
		return "not"
	if request.method == "POST":
		name = request.form['username']
		password = request.form['password']
		if Users.query.filter_by(username=name).first():
			flash('user already there', 'error')
			return redirect('/register')
		create = Users(username=name, password=password)
		db.session.add(create)
		db.session.commit()
		flash('sucess creste user', 'sus')

		return redirect('/login')
	return render_template('create_user.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	if 'name' in session: 
		return redirect('/')
	if request.method == "POST":
		name = request.form['username']
		password = request.form['password']
		user = Users.query.filter_by(username=name).first()
		if not user:
			flash('wrong username', 'error')
			return redirect('/login')
		if not check_password_hash(user.password, password): 
			flash('wrong password', 'error')
			return redirect('/login')
		flash('sucess Login', 'sus')
		session['name'] = name
		return redirect('/')
	return render_template('create_user.html')
@app.route('/')
def sessions():
	if not 'name' in session:
		return redirect('/login')
	print(session['name'])
	return render_template('session.html', sesi=session['name'])





def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')



@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
	if not 'to' in json:
		 socketio.emit('input_error', {'msg': 'error'}, callback=messageReceived)
	else:
		 to = Users.query.filter_by(username=json['to'])
		 if not  to.first():
			 socketio.emit('error', {'msg': 'error', 'you': session['name']}, callback=messageReceived)
		 else:
			 if json["to"] == session['name']:
					socketio.emit('error', {'msg': 'To error'}, callback=messageReceived)
			 else:
				 json['you'] = session['name']
				 add_d = Chat(**json)
				 db.session.add(add_d)
				 db.session.commit()
				 if json['to'] == session['name']: 
						 socketio.emit('my response', json, callback=messageReceived)
				 elif json['you'] == session['name']: 
						 socketio.emit('my response', json, callback=messageReceived)
				 else:
					 print('ada')
					   


			

@app.route('/logout')
def logout(): 
	if not  'name' in session:
		return redirect('/login')
	session.pop('name')
	return redirect('/login')



@app.cli.command("migrate")
@click.argument("name")
def create_user(name): 	
	 if name == 'drop':
		 db.drop_all()
		 print('sucess Delete Table')
	 elif name == 'add': 
		 db.create_all()
		 print('sucess create Table')
	 else:
		 print('error')

if __name__ == '__main__':
    socketio.run(app, debug=True)
	