from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import xml.etree.ElementTree as ET
import os, sys, urllib.request

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db=SQLAlchemy(app)
link='https://maps.googleapis.com/maps/api/staticmap?markers={}&size=460x460&key=AIzaSyCic4Gp4eox33x5zUB5wMJEOdCr3632PVE'


class Drawing(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.Text())
    drawing=db.Column(db.Text())
    date=db.Column(db.DateTime())
    coordinates=db.Column(db.Text())
    def __init__(self, title, drawing, coordinates):
        self.title = title
        self.drawing = drawing
        self.date = datetime.now()
        self.coordinates=coordinates
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
            xml_file=urllib.request.urlopen("http://ip-api.com/xml/{}".format(request.headers['X-Forwarded-For']))
            root=ET.parse(xml_file).getroot()
            coordinates = root[7].text + ',' + root[8].text
            element= Drawing(title, drawing, coordinates)
            db.session.add(element)
        if deleted:
            db.session.delete(Drawing.query.filter_by(id=deleted).first())
        db.session.commit()
    markers=''
    drawings=Drawing.query.order_by(Drawing.date.desc()).limit(10).all()

    for drawing in drawings:
        coordinates=drawing.coordinates
        if coordinates:
            if not markers:
                markers=drawing.coordinates
            else:
                markers+='|'+coordinates

    return render_template('doc.html',drawings=drawings, map=link.format(markers))

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
