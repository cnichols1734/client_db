from datetime import datetime
import string
import secrets
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import timedelta

app = Flask(__name__)
app.secret_key = '17341734'
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

# Initialize the LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Create the User class
class User(UserMixin):
    id = 1
    username = "admin"
    password = "Cassiechris177!"

# User loading and validation functions
@login_manager.user_loader
def load_user(user_id):  # Add the user_id argument
    if int(user_id) == User.id:
        return User()
    return None

def validate_user(username, password):
    return username == User.username and password == User.password

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_user(username, password):
            user = User()
            login_user(user, remember=True)
            return redirect(url_for('index'))
    return render_template('login.html')

DATE_FORMAT = '%Y-%m-%d'


@app.template_filter('date')
def format_date(value, format='%-m/%-d/%Y'):
    return value.strftime(format)


def parse_date(date_str, format=DATE_FORMAT):
    return datetime.strptime(date_str, format).date() if date_str else None


def generate_unique_uuid(length=6):
    alphabet = string.ascii_letters + string.digits
    while True:
        new_uuid = ''.join(secrets.choice(alphabet) for _ in range(length))
        if Property.query.filter_by(uuid=new_uuid).count() == 0:
            break
    return new_uuid


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)

    property_detail = db.relationship('Property', backref='client', uselist=False)

    def __repr__(self):
        return f"<Client {self.client_name}>"


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    uuid = db.Column(db.String(6), nullable=False, unique=True, default=generate_unique_uuid)
    street_address = db.Column(db.String(100), nullable=False)
    option_period_expires = db.Column(db.Date, nullable=True)
    survey_provided_by = db.Column(db.String(50), nullable=True)
    survey_due_date = db.Column(db.Date, nullable=True)
    buyer_financing_deadline = db.Column(db.Date, nullable=True)
    appraisal = db.Column(db.Date, nullable=True)
    buyer_final_walkthrough = db.Column(db.Date, nullable=True)
    agreed_upon_repairs = db.Column(db.Date, nullable=True)
    closing_date = db.Column(db.Date, nullable=True)

    client_property = db.relationship('Client', backref=db.backref('properties', lazy=True))


@app.route('/add', methods=['POST'])
def add_client():
    client = Client(client_name=request.form['client_name'])
    db.session.add(client)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/update/<int:id>', methods=['POST'])
def update_client(id):
    client = db.session.get(Client, id)
    client.client_name = request.form['new_client_name']
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/client/<uuid>')
def client(uuid):
    property = Property.query.filter_by(uuid=uuid).first_or_404()
    client = property.client
    return render_template('client.html', client=client)


@app.route('/add_property/<int:client_id>', methods=['POST'])
def add_property(client_id):
    client = db.session.get(Client, client_id)
    if client is None:
        abort(404)
    property = Property(
        client_id=client.id,
        street_address=request.form['street_address'],
        option_period_expires=parse_date(request.form['option_period_expires']),
        survey_provided_by=request.form['survey_provided_by'],
        survey_due_date=parse_date(request.form['survey_due_date']),
        buyer_financing_deadline=parse_date(request.form['buyer_financing_deadline']),
        appraisal=parse_date(request.form['appraisal']),
        buyer_final_walkthrough=parse_date(request.form['buyer_final_walkthrough']),
        agreed_upon_repairs=parse_date(request.form['agreed_upon_repairs']),
        closing_date=parse_date(request.form['closing_date'])
    )
    db.session.add(property)
    db.session.commit()
    return redirect(url_for('index'))



@app.route('/update_property/<int:id>', methods=['GET', 'POST'])
def update_property(id):
    property = db.session.get(Property, id)
    if property is None:
        abort(404)

    if request.method == 'POST':
        property.street_address = request.form['street_address']
        property.option_period_expires = parse_date(request.form['option_period_expires'])
        property.survey_provided_by = request.form['survey_provided_by']
        property.survey_due_date = parse_date(request.form['survey_due_date'])
        property.buyer_financing_deadline = parse_date(request.form['buyer_financing_deadline'])
        property.appraisal = parse_date(request.form['appraisal'])
        property.buyer_final_walkthrough = parse_date(request.form['buyer_final_walkthrough'])
        property.agreed_upon_repairs = parse_date(request.form['agreed_upon_repairs'])
        property.closing_date = parse_date(request.form['closing_date'])

        db.session.commit()
        return redirect(url_for('client', uuid=property.uuid))

    return jsonify(
        id=property.id,
        street_address=property.street_address,
        option_period_expires=property.option_period_expires.strftime(DATE_FORMAT) if property.option_period_expires else None,
        survey_provided_by=property.survey_provided_by,
        survey_due_date=property.survey_due_date.strftime(DATE_FORMAT) if property.survey_due_date else None,
        buyer_financing_deadline=property.buyer_financing_deadline.strftime(DATE_FORMAT) if property.buyer_financing_deadline else None,
        appraisal=property.appraisal.strftime(DATE_FORMAT) if property.appraisal else None,
        buyer_final_walkthrough=property.buyer_final_walkthrough.strftime(DATE_FORMAT) if property.buyer_final_walkthrough else None,
        agreed_upon_repairs=property.agreed_upon_repairs.strftime(DATE_FORMAT) if property.agreed_upon_repairs else None,
        closing_date=property.closing_date.strftime(DATE_FORMAT) if property.closing_date else None
    )



@app.route('/delete_client_and_property/<int:id>', methods=['POST'])
def delete_client_and_property(id):
    # First, delete the associated property if it exists
    property = Property.query.filter_by(client_id=id).first()
    if property:
        db.session.delete(property)

    # Then, delete the client
    client = db.session.get(Client, id)
    if client is None:
        abort(404)
    db.session.delete(client)
    db.session.commit()

    return redirect(url_for('index'))



@app.route('/clients/property_count')
def get_property_counts():
    clients = Client.query.all()
    client_property_counts = {}
    for client in clients:
        client_property_counts[client.id] = len(client.properties)
    return jsonify(client_property_counts)


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('public_home'))
    clients = Client.query.all()
    return render_template('index.html', clients=clients)


@app.route('/client/<int:client_id>')
@login_required
def client_property(client_id):
    client = db.session.get(Client, client_id)
    if client is None:
        abort(404)
    return render_template('client_property.html', client=client)


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/public')
def public_home():
    return render_template('public_home.html')


def main():
    login_manager.login_view = 'login'
    app.run(debug=True, host='0.0.0.0', port=5001)

if __name__ == '__main__':
    main()





