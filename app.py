from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os,sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:hello@localhost/ascii_db"
db=SQLAlchemy(app)

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

db.create_all()
db.session.commit()

@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='POST':
        title=request.form.get('title')
        drawing=request.form.get('drawing')
        deleted=request.form.get('deleted')
        if title and drawing:
            element= Drawing(title, drawing)
            db.session.add(element)
        if deleted:
            db.session.delete(Drawing.query.filter_by(id=deleted).first())
        db.session.commit()

    return render_template('doc.html',drawings=Drawing.query.all())

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
