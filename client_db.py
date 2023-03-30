from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

DATE_FORMAT = '%Y-%m-%d'


@app.template_filter('date')
def format_date(value, format='%-m/%-d/%Y'):
    return value.strftime(format)


def parse_date(date_str, format=DATE_FORMAT):
    return datetime.strptime(date_str, format).date() if date_str else None


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)

    property_detail = db.relationship('Property', backref='client', uselist=False)

    def __repr__(self):
        return f"<Client {self.client_name}>"


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
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


@app.route('/')
def index():
    clients = Client.query.all()
    return render_template('index.html', clients=clients)


@app.route('/add', methods=['POST'])
def add_client():
    client = Client(client_name=request.form['client_name'])
    db.session.add(client)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/update/<int:id>', methods=['POST'])
def update_client(id):
    client = Client.query.get(id)
    client.client_name = request.form['client_name']
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/client/<int:id>')
def client(id):
    client = Client.query.get_or_404(id)
    return render_template('client_property.html', client=client)


@app.route('/add_property/<int:client_id>', methods=['POST'])
def add_property(client_id):
    client = Client.query.get_or_404(client_id)
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
    property = Property.query.get_or_404(id)

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
        return redirect(url_for('client', id=property.client_id))

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


@app.route('/delete_client/<int:id>', methods=['POST'])
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete_property/<int:id>', methods=['POST'])
def delete_property(id):
    property = Property.query.get_or_404(id)
    client_id = property.client_id
    db.session.delete(property)
    db.session.commit()
    return redirect(url_for('client', id=client_id))


@app.route('/clients/property_count')
def get_property_counts():
    clients = Client.query.all()
    client_property_counts = {}
    for client in clients:
        client_property_counts[client.id] = len(client.properties)
    return jsonify(client_property_counts)


def main():
    with app.app_context():
        db.create_all()
    app.run(debug=True)


if __name__ == '__main__':
    main()


