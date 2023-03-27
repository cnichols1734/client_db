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

    property_detail = db.relationship('Property', backref='client', uselist=False)

    @property
    def property_name(self):
        if self.property_detail:
            return self.property_detail.street_name
        else:
            return "No Property Added"

    def __repr__(self):
        return f"<Client {self.client_name}>"


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    street_address = db.Column(db.String(100), nullable=False)
    street_name = db.Column(db.String(100))
    zip_code = db.Column(db.String(10))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    property_type = db.Column(db.String(20))
    price = db.Column(db.Float)
    build_year = db.Column(db.Integer)

    client_property = db.relationship('Client', backref=db.backref('properties', lazy=True))

    @property
    def name(self):
        return f"{self.street_address} {self.street_name}"


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
        client_end_date=datetime.strptime(request.form['client_end_date'], '%Y-%m-%d').date() if request.form[
            'client_end_date'] else None,
        client_inspection_date=datetime.strptime(request.form['client_inspection_date'], '%Y-%m-%d').date() if
        request.form['client_inspection_date'] else None,
        client_closing_date=datetime.strptime(request.form['client_closing_date'], '%Y-%m-%d').date() if request.form[
            'client_closing_date'] else None
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
    client.client_end_date = datetime.strptime(request.form['client_end_date'], '%Y-%m-%d').date() if request.form[
        'client_end_date'] else None
    client.client_inspection_date = datetime.strptime(request.form['client_inspection_date'], '%Y-%m-%d').date() if \
    request.form['client_inspection_date'] else None
    client.client_closing_date = datetime.strptime(request.form['client_closing_date'], '%Y-%m-%d').date() if \
    request.form['client_closing_date'] else None
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/client/<int:id>')
def client(id):
    client = Client.query.get_or_404(id)
    return render_template('client.html', client=client)


@app.route('/add_property/<int:client_id>', methods=['POST'])
def add_property(client_id):
    client = Client.query.get_or_404(client_id)
    property = Property(
        client_id=client.id,
        street_address=request.form['street_address'],
        street_name=request.form['street_name'],
        zip_code=request.form['zip_code'],
        city=request.form['city'],
        state=request.form['state'],
        property_type=request.form['property_type'],
        price=float(request.form['price']),
        build_year=request.form['build_year']
    )
    db.session.add(property)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
