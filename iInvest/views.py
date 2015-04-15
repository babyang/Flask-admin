#coding:utf-8
from iInvest import app, db
from flask import render_template,flash,redirect, request, abort, url_for, session, jsonify
from forms import LoginForm, RegistrationForm, ProductForm, TrustProductForm
import datetime
from models import Product, Preorder, TrustProduct, TrustProductPreorder
import json
import flask

    	
@app.route('/')
@app.route('/index')
def index():
	user={'nickname':'MM'}
	posts=[
	{'author':{'nickname':'John'},
	 'body':'Beautiful day in Portland!'
	},
	{'author':{'nickname':'Susan'},
	 'body':'The Avengers movie was so cool!'
	}
	]
	return render_template('index.html',user=user,title='Home',posts=posts)

# @app.route('/login', methods = ['GET', 'POST'])
# def login():
# 	form = LoginForm()
# 	if form.validate_on_submit():
# 		flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
#         return redirect('/index')
# 	return render_template('login.html',title = 'Sign In',form = form)

@app.route('/login')
def login():
	return render_template('signin.html')

@app.route('/hello/', methods=['POST'])
def hello():
    name=request.form['yourname']
    password=request.form['password']
    if name=='admin' and password=='admin':
    	flash('you are logged in!')
    	session['admin_logged']=True
    	return redirect(url_for('get_trust_products'))

@app.route('/logout')
def logout():
	session.pop('admin_logged', None)
	flash('Logged out!')
	return redirect(url_for('get_trust_products'))

@app.after_request
def add_header(response):
	response.headers['Access-Control-Allow-Origin']='*'
	return response

@app.route('/register', methods=['GET','POST'])
def register():
	form=RegistrationForm(request.form)
	if request.method=='POST' and form.validate():
		user=User(form.username.data,form.email.data,form.password.data)
		db.add(user)
		db.commit()
		flash('Thanks for registering')
		return redirect(url_for('login'))
	return render_template('register.html', form=form)

@app.route('/products', methods=['GET'])
def get_products():
	# p=Product(name='sadfasdf', threshold=12100, dueTime='asdasd', shortDesc='123123', profitRate='123123', profitType='1231231', profitDesc='123123', status='123123',organization='123132',investType='123123',investArea='123123',total=2300,detailDesc='asd',riskControl=1)
	# db.session.add(p)
	# db.session.commit()
	products=Product.query.all()
	if 'json'!=request.args.get('format'):
		return render_template('products.html',products=products)
	else:
		productsList=[]
		for product in products:
			productsList.append(Product.product2dict(product))
		return json.dumps(productsList, ensure_ascii=False).encode('utf8')

@app.route('/products', methods=['POST'])
def create_product():
	form=ProductForm(request.form)
	p=Product(name=form.name.data, threshold=form.threshold.data, dueTime=form.dueTime.data, shortDesc=form.shortDesc.data, profitRate=form.profitRate.data, profitType=form.profitType.data, profitDesc=form.profitDesc.data, status=form.status.data,organization=form.organization.data,investType=form.investType.data,investArea=form.investArea.data,total=form.total.data,detailDesc=form.detailDesc.data,riskControl=form.riskControl.data)
	db.session.add(p)
	db.session.commit()
	flash('Add product successfully!')
	return redirect(url_for('create_product'))

@app.route('/product/<id>')
def product(id):
	product=Product.query.filter_by(id=id).first()
	#if product == None:
    #	flash('Product ' + id + ' not found.')
    #    return redirect(url_for('index'))
	if 'json'!=request.args.get('format'):
		return render_template('product.html', product=product)
	else:
		return json.dumps(product, default=Product.product2dict, ensure_ascii=False).encode('utf8')

@app.route('/preorders/', methods=['GET'])
def get_preorders():
	preorders=Preorder.query.all()
	return render_template('preorders.html', preorders=preorders)

@app.route('/preorders/', methods=['POST'])
def create_preorders():
	if not request.form or not 'product_id' in request.form or not 'customer_name' in request.form or not 'customer_phone' in request.form:
		abort(400)
	preorder=Preorder(request.form['customer_name'],request.form['customer_phone'],request.form['product_id'])
	db.session.add(preorder)
	db.session.commit()
	flash('Add preorder successfully!')
	return redirect(url_for('create_preorders'))
#@csrt.exempt
@app.route('/preorders/json', methods=['POST'])
def json_create_preorders():
	#print request
	print 'test'
	#print request.json
	print request.mimetype
	print request.json
	print 'aaa',request.get_json(force=True)
	print request.json['product_id']
	if not request.json or not 'product_id' in request.json or not 'customer_name' in request.json or not 'customer_phone' in request.json:
		abort(400)
	preorder=Preorder(request.json['customer_name'],request.json['customer_phone'],request.json['product_id'])
	db.session.add(preorder)
	db.session.commit()
	return jsonify({'status':'success'}), 201

###############信托产品#########################
@app.route('/trustProducts', methods=['GET'])
def get_trust_products():
	product_list=TrustProduct.query.with_entities(TrustProduct.id, TrustProduct.name, TrustProduct.reason, \
		TrustProduct.threshold,TrustProduct.dueTime,TrustProduct.profitRate).all()
	productsList=[]
	for product in product_list:
		productsList.append({'id':product[0],'name':product[1],'reason':product[2],'threshold':product[3],'dueTime':product[4],'profitRate':product[5]})
	if 'json'!=request.args.get('format'):
		return render_template('trustProducts.html',products=productsList)
	else:
		return json.dumps(productsList, ensure_ascii=False).encode('utf8')

@app.route('/trustProducts', methods=['POST'])
def create_trust_product():
	form=TrustProductForm(request.form)
	print form.reason.data
	p=TrustProduct(name=form.name.data, reason=form.reason.data, threshold=form.threshold.data, dueTime=form.dueTime.data, \
		shortDesc=form.shortDesc.data, profitRate=form.profitRate.data, profitType=form.profitType.data, profitClose=form.profitClose.data, \
		profitDesc=form.profitDesc.data, status=form.status.data,organization=form.organization.data,investType=form.investType.data,\
		investArea=form.investArea.data,total=form.total.data, detailDesc=form.detailDesc.data,riskControl=form.riskControl.data)
	db.session.add(p)
	db.session.commit()
	flash('Add trust product successfully!')
	return redirect(url_for('create_trust_product'))

@app.route('/trustProduct/<id>', methods=['GET'])
def trust_product(id):
	product=TrustProduct.query.filter_by(id=id).first()
	if 'json'!=request.args.get('format'):
		return render_template('trustProduct.html', product=product)
	else:
		return json.dumps(product, default=TrustProduct.product2dict, ensure_ascii=False).encode('utf8')

@app.route('/trustProduct/<id>', methods=['DELETE'])
def delete_trust_product(id):
	TrustProduct.query.filter_by(id=id).delete()
	db.session.commit()
	flash('Delete trust product successfully!')
	return '201'

@app.route('/trustPreorders/', methods=['GET'])
def get_trust_preorders():
	preorders=TrustProductPreorder.query.all()
	return render_template('trustPreorders.html', preorders=preorders)

@app.route('/trustPreorders/', methods=['POST'])
def create_trust_preorders():
	if not request.form or not 'product_id' in request.form or not 'customer_name' in request.form or not 'customer_phone' in request.form:
		abort(400)
	preorder=TrustProductPreorder(request.form['customer_name'],request.form['customer_phone'],request.form['product_id'])
	db.session.add(preorder)
	db.session.commit()
	flash('Add preorder successfully!')
	return redirect(url_for('create_trust_preorders'))

@app.route('/trustPreorders/json', methods=['POST'])
def json_create_trust_preorders():
	if not request.json or not 'product_id' in request.json or not 'customer_name' in request.json or not 'customer_phone' in request.json:
		abort(400)
	preorder=TrustProductPreorder(request.json['customer_name'],request.json['customer_phone'],request.json['product_id'])
	db.session.add(preorder)
	db.session.commit()
	return jsonify({'status':'success'}), 201