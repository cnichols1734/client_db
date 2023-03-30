from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)


@app.template_filter('date')
def format_date(value, format='%B %d, %Y'):
    return value.strftime(format)


CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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
        option_period_expires=datetime.strptime(request.form['option_period_expires'], '%Y-%m-%d').date() if
        request.form['option_period_expires'] else None,
        survey_provided_by=request.form['survey_provided_by'],
        survey_due_date=datetime.strptime(request.form['survey_due_date'], '%Y-%m-%d').date() if request.form[
            'survey_due_date'] else None,
        buyer_financing_deadline=datetime.strptime(request.form['buyer_financing_deadline'], '%Y-%m-%d').date() if
        request.form['buyer_financing_deadline'] else None,
        appraisal=datetime.strptime(request.form['appraisal'], '%Y-%m-%d').date() if request.form[
            'appraisal'] else None,
        buyer_final_walkthrough=datetime.strptime(request.form['buyer_final_walkthrough'], '%Y-%m-%d').date() if
        request.form['buyer_final_walkthrough'] else None,
        agreed_upon_repairs=datetime.strptime(request.form['agreed_upon_repairs'], '%Y-%m-%d').date() if request.form[
            'agreed_upon_repairs'] else None,
        closing_date=datetime.strptime(request.form['closing_date'], '%Y-%m-%d').date() if request.form[
            'closing_date'] else None
    )
    db.session.add(property)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/update_property/<int:id>', methods=['GET', 'POST'])
def update_property(id):
    property = Property.query.get_or_404(id)

    if request.method == 'POST':
        property.street_address = request.form['street_address']
        property.option_period_expires = datetime.strptime(request.form['option_period_expires'], '%Y-%m-%d').date() if \
            request.form['option_period_expires'] else None
        property.survey_provided_by = request.form['survey_provided_by']
        property.survey_due_date = datetime.strptime(request.form['survey_due_date'], '%Y-%m-%d').date() if \
            request.form['survey_due_date'] else None
        property.buyer_financing_deadline = datetime.strptime(request.form['buyer_financing_deadline'],
                                                              '%Y-%m-%d').date() if request.form[
            'buyer_financing_deadline'] else None
        property.appraisal = datetime.strptime(request.form['appraisal'], '%Y-%m-%d').date() if request.form[
            'appraisal'] else None
        property.buyer_final_walkthrough = datetime.strptime(request.form['buyer_final_walkthrough'],
                                                             '%Y-%m-%d').date() if request.form[
            'buyer_final_walkthrough'] else None
        property.agreed_upon_repairs = datetime.strptime(request.form['agreed_upon_repairs'], '%Y-%m-%d').date() if \
            request.form['agreed_upon_repairs'] else None
        property.closing_date = datetime.strptime(request.form['closing_date'], '%Y-%m-%d').date() if request.form[
            'closing_date'] else None

        db.session.commit()
        return redirect(url_for('client', id=property.client_id))

    return jsonify(
        id=property.id,
        street_address=property.street_address,
        option_period_expires=property.option_period_expires.strftime(
            '%Y-%m-%d') if property.option_period_expires else None,
        survey_provided_by=property.survey_provided_by,
        survey_due_date=property.survey_due_date.strftime('%Y-%m-%d') if property.survey_due_date else None,
        buyer_financing_deadline=property.buyer_financing_deadline.strftime(
            '%Y-%m-%d') if property.buyer_financing_deadline else None,
        appraisal=property.appraisal.strftime('%Y-%m-%d') if property.appraisal else None,
        buyer_final_walkthrough=property.buyer_final_walkthrough.strftime(
            '%Y-%m-%d') if property.buyer_final_walkthrough else None,
        agreed_upon_repairs=property.agreed_upon_repairs.strftime('%Y-%m-%d') if property.agreed_upon_repairs else None,
        closing_date=property.closing_date.strftime('%Y-%m-%d') if property.closing_date else None
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
    return client_property_counts



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
