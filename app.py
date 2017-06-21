from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from collections import namedtuple
import xml.etree.ElementTree as ET
import os, sys, urllib.request, redis, json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db=SQLAlchemy(app)
r=redis.from_url(os.environ['REDIS_URL'])
r.flushall()
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
    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'drawing': self.drawing,
            'date': self.drawing,
            'coordinates': self.coordinates
        }

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
            db.session.refresh(element)
            r.lpush('drawings',json.dumps(element.as_dict()))
            if r.llen('drawings')>10:
                r.rpop('drawings')

        if deleted:
            db.session.delete(Drawing.query.filter_by(id=deleted).first())
            drawings=Drawing.query.order_by(Drawing.date.desc()).limit(10).all()
            print("DEL OPERATION, DB HIT")
            jsons=[json.dumps(d.as_dict()) for d in drawings]
            r.delete('drawings')
            r.rpush('drawings',*jsons)


        db.session.commit()
        return redirect('/')

    markers=''

    drawings_jsons=r.lrange('drawings',0,-1)

    print('REDIS HIT, Exists in cache?', drawings_jsons==True)
    if not drawings_jsons:
        drawings=Drawing.query.order_by(Drawing.date.desc()).limit(10).all()
        print('DB HIT')
        r.rpush('drawings',*[json.dumps(d.as_dict()) for d in drawings])

    drawings_jsons=r.lrange('drawings',0,-1)
    drawings = [json2drawing(drawing_json) for drawing_json in drawings_jsons]
    for drawing in drawings:
        coordinates=drawing.coordinates
        if coordinates:
            if not markers:
                markers=drawing.coordinates
            else:
                markers+='|'+coordinates

    return render_template('doc.html',drawings=drawings, map=link.format(markers))

def json2drawing(s):
    d=json.loads(s)
    obj=Drawing(d['title'], d['drawing'], d['coordinates'])
    obj.id=d['id']
    return obj

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
