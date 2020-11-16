from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import MetaData

# import db & models
from models import db, ExampleModel

app = Flask(__name__.split('.')[0])
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
valid_tags = {}
db.init_app(app)


#base python object for each entry in the sql database
class food_item(db.Model):
    id = db.Column(db.Integer, primary_key = True )
    tag = db.Column(db.String(20), unique = False)
    item_name = db.Column(db.String(30), unique = False)
    
    def __repr__(self):
        return '<Tag %r>' % self.tag + '<Food %r>' % self.item_name

@app.route("/api/example", methods=["GET", "POST", "PUT", "DELETE"])
def ExampleEndpoint():
    result = db.session.query(ExampleModel).filter(ExampleModel.number > 1)
    
    return {
        "results": [(dict(row.items())) for row in result]
    }, 200


#function adds a new tag
@app.route("/insert/tag")
def newTag():
    input_tag = request.args['input_tag']
    if(input_tag in valid_tags):
        raise Exception("Attempted to create tag that already exists")
    
    #no objects with that tag yet
    valid_tags[input_tag] = 0
    return "Success"
    

#create item with existing tag
@app.route("/insert/item_tag")
def insert_item():
    input_tag = request.args['input_tag']
    new_item = request.args['new_item']
    if(input_tag not in valid_tags):
        raise Exception("Attempted to input tag that doesn't exists")
    
    nextFood = food_item(tag = input_tag, item_name = new_item)
    db.session.add(nextFood)
    db.session.commit()
    valid_tags[input_tag] += 1
    return "Success"
    
#create item with only name, no tag
@app.route("/insert/item")
def insert_item_only():
    new_item = request.args['new_item']
    nextFood = food_item(tag = "", item_name = new_item)
    db.session.add(nextFood)
    db.session.commit()
    return "Success"


#read all items with existing tag
@app.route("/read/tag")
def read_tag():
    input_tag = request.args['input_tag']
    return str(food_item.query.filter_by(tag = input_tag).all())
    
#change the tag for one item
@app.route("/update/item")
def change_tag():
    new_tag = request.args['new_tag']
    old_tag = request.args['old_tag']
    name = request.args['item_name']
    
    #finds the old item
    res = food_item.query.filter(food_item.tag == old_tag, food_item.item_name == name).first()
    
    #checks that the old item is valid
    if(res is None):
        raise Exception("Attempted to update tag for item that doesn't exist")
    
    res.tag = new_tag
    db.session.commit()
    return "Success"
    
#delete a item-tag
@app.route("/delete/item")
def delete_item():
    tag = request.args['input_tag']
    name = request.args['item_name']
    res = food_item.query.filter(food_item.tag == tag, food_item.item_name == name).first()
    if(res is None):
        raise Exception("Attempted to delete item-tag that doesn't exist")
    db.session.delete(res)
    db.session.commit()
    return "Success"
    
#delete a tag
@app.route("/delete/tag")
def delete_tag():
    tag = request.args['input_tag']
    if(tag not in valid_tags):
        raise Exception("Attempted to tag item that doesn't exist")
    del valid_tags[tag]
    return "Success"

#returns all items in string form
@app.route("/displayall")
def display():
    print(food_item.query.all())
    return str(food_item.query.all())

with app.app_context():
	db.create_all()

if __name__ == "__main__":
    app.run()
