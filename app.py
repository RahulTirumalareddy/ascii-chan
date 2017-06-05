from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:hello@localhost/ascii_db"
db=SQLAlchemy(app)
drawings=Drawing.query.all()

class Drawing(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.Text())
    drawing=db.Column(db.Text())
    date=db.Column(db.DateTime())
    def __init__(self, title, drawing):
        self.title = title
        self.drawing = drawing
        self.date = datetime.now()
    def __repr__(self):
        return '<ID %s>' % self.id

@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='POST':
        element= Drawing(request.form['title'], request.form['drawing'])
        db.session.add(element)
        db.session.commit()

    return render_template('doc.html')

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
