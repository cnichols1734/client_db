from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_phone_number = db.Column(db.String(15), nullable=False)
    client_start_date = db.Column(db.Date, nullable=False)
    client_end_date = db.Column(db.Date, nullable=True)
    client_inspection_date = db.Column(db.Date, nullable=True)
    client_closing_date = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"<Client {self.client_name}>"

@app.route('/')
def index():
    clients = Client.query.all()
    return render_template('index.html', clients=clients)

@app.route('/add', methods=['POST'])
def add_client():
    client = Client(
        client_name=request.form['client_name'],
        client_phone_number=request.form['client_phone_number'],
        client_start_date=datetime.strptime(request.form['client_start_date'], '%Y-%m-%d').date(),
        client_end_date=datetime.strptime(request.form['client_end_date'], '%Y-%m-%d').date() if request.form['client_end_date'] else None,
        client_inspection_date=datetime.strptime(request.form['client_inspection_date'], '%Y-%m-%d').date() if request.form['client_inspection_date'] else None,
        client_closing_date=datetime.strptime(request.form['client_closing_date'], '%Y-%m-%d').date() if request.form['client_closing_date'] else None
    )
    db.session.add(client)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['POST'])
def update_client(id):
    client = Client.query.get(id)
    client.client_name = request.form['client_name']
    client.client_phone_number = request.form['client_phone_number']
    client.client_start_date = datetime.strptime(request.form['client_start_date'], '%Y-%m-%d').date()
    client.client_end_date = datetime.strptime(request.form['client_end_date'], '%Y-%m-%d').date() if request.form['client_end_date'] else None
    client.client_inspection_date = datetime.strptime(request.form['client_inspection_date'], '%Y-%m-%d').date() if request.form['client_inspection_date'] else None
    client.client_closing_date = datetime.strptime(request.form['client_closing_date'], '%Y-%m-%d').date() if request.form['client_closing_date'] else None
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/client/<int:id>')
def client(id):
    client = Client.query.get_or_404(id)
    return render_template('client.html', client=client)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)





