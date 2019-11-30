from flask import Flask,redirect,url_for,render_template,request,flash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

cnx = mysql.connector.connect(user='root',password='root', database='frappedb')
cursor = cnx.cursor(buffered=True)

def is_empty(val):
	if val == "" or val == 0 or val == '' or len(val) == 0 or len == None:
		return True
	return False

def qty_at_loc(product_id,location_id,movement_id=None):
	pos=neg=None
	pos_str = '''select sum(qty) from productmovement where product_id=%s and to_location=%s'''
	neg_str = '''select sum(qty) from productmovement where product_id=%s and from_location=%s'''

	if(movement_id):
		pos_str += ' and movement_id<' + movement_id
		neg_str += ' and movement_id<' + movement_id

	cursor.execute(pos_str,(product_id,location_id))
	for (qty,) in cursor:
		pos = qty
	cursor.execute(neg_str,(product_id,location_id))
	for (qty,) in cursor:
		neg = qty

	if(not neg):
		neg=0
	if(not pos):
		pos=0
	return pos-neg


@app.route('/products',methods=['GET','POST'])
def products():
	cursor.execute('''select * from product''')
	products=[]
	return render_template('products.html',products=cursor)

@app.route('/products/add',methods=['GET','POST'])
def products_add():
	if request.method == 'POST':
		product_name = request.form['product_name'];
		try:	
			assert(not is_empty(product_name))
			cursor.execute('''insert into product (product_name) values (%s)''',(product_name,))
			cnx.commit()
			flash("Product added successfully.",'success')
			return redirect(url_for('products'))
		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
			flash("Something went wrong",'error')
			redirect(url_for('products_add'))
		except:
			msg = "Product Name cannot be empty."
			print(msg)
			flash(msg,'error')
			return redirect(url_for('products_add'))

	return render_template('products_add.html')

@app.route('/products/<product_id>')
def products_view(product_id):
	# if req.method=="POST":

		# edit the product_id
	#else get product details
	cursor.execute('''select * from product where product_id=%s''',(product_id,))
	return render_template('products_view.html',products=cursor)

@app.route('/products/<product_id>/edit',methods=['GET','POST'])
def products_edit(product_id):
	if request.method == 'POST':
		try:
			product_name=request.form['product_name']
			assert(not is_empty(product_name))
			if(product_name):
				cursor.execute('''update product set product_name = %s where product_id = %s''',(product_name,product_id))
				cnx.commit()
				flash("Product edited successfully.",'success')
				return redirect(url_for('products'))

		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
			flash("Something went wrong",'error')

		except:
			msg = "Product Name cannot be empty."
			print(msg)
			flash(msg,'error')
			return redirect(url_for('products_edit',product_id=product_id))

	cursor.execute('''select * from product where product_id=%s''',(product_id,))
	return render_template('products_edit.html',products=cursor,product_id=product_id)

@app.route('/products/<product_id>/delete')
def products_delete(product_id):
	try:
		cursor.execute('''delete from product where product_id=%s''',(product_id,))
		cnx.commit()
		flash("Product deleted successfully!",'success')
		return redirect(url_for('products'))
	except mysql.connector.Error as err: 
		print("Something went wrong: {}".format(err))
		flash("Something went wrong",'error')
		return redirect(url_for('products_edit',product_id=product_id))

# Locatin routes


@app.route('/locations',methods=['GET','POST'])
def locations():
	cursor.execute('''select * from location''')
	return render_template('locations.html',locations=cursor)

@app.route('/locations/add',methods=['GET','POST'])
def locations_add():
	if request.method == 'POST':
		location_name = request.form['location_name'];
		try:	
			assert(not is_empty(location_name))
			cursor.execute('''insert into location (location_name) values (%s)''',(location_name,))
			cnx.commit()
			flash("Location added successfully.",'success')
			return redirect(url_for('locations'))
		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
			flash("Something went wrong",'error')
			redirect(url_for('locations_add'))
		except:
			msg = "location Name cannot be empty."
			print(msg)
			flash(msg,'error')
			return redirect(url_for('locations_add'))

	return render_template('locations_add.html')

@app.route('/locations/<location_id>')
def locations_view(location_id):
	# if req.method=="POST":

		# edit the location_id
	#else get location details
	cursor.execute('''select * from location where location_id=%s''',(location_id,))
	return render_template('locations_view.html',locations=cursor)

@app.route('/locations/<location_id>/edit',methods=['GET','POST'])
def locations_edit(location_id):
	if request.method == 'POST':
		try:
			location_name=request.form['location_name']
			assert(not is_empty(location_name))
			cursor.execute('''update location set location_name = %s where location_id = %s''',(location_name,location_id))
			cnx.commit()
			flash("Location edited successfully.",'success')
			return redirect(url_for('locations'))
					
		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
			flash("Something went wrong",'error')

		except:
			msg = "location Name cannot be empty."
			print(msg)
			flash(msg,'error')
			return redirect(url_for('locations_edit',location_id=location_id))

	cursor.execute('''select * from location where location_id=%s''',(location_id,))
	return render_template('locations_edit.html',locations=cursor,location_id=location_id)

@app.route('/locations/<location_id>/delete')
def locations_delete(location_id):
	try:
		cursor.execute('''delete from location where location_id=%s''',(location_id,))
		flash("Location deleted successfully!",'success')
		cnx.commit()
		return redirect(url_for('locations'))
	except mysql.connector.Error as err: 
		print("Something went wrong: {}".format(err))
		flash("Something went wrong",'error')
		return redirect(url_for('locations_edit',location_id=location_id))

@app.route('/movements',methods=['GET','POST'])
def movements():
	if request.method == "POST":
		try:
			from_location = request.form['from_location']
			to_location = request.form['to_location']
			product_id = request.form['product_id']
			qty = int(request.form['qty'])
			timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

			if(from_location == to_location and not(is_empty(from_location)) and not(is_empty(to_location))):
				flash("Please select different locations",'error')
				return redirect(url_for('movements'))

			# for qty first we check whether there already exists a product for given location.
			# Three cases - 
			# Only from location, then search for product and from location and fetch qty, new qty = old qty-1
			# Only to location, then search for product and to location and new qty = old qty + 1
			# Two location, then search for product and check whether the from location has product qty>0. And then update the qty there and update the quantity
			# at new location
			assert(not is_empty(from_location) or not is_empty(to_location))
			# Case 1
			if(is_empty(to_location)):
				if(qty_at_loc(product_id,from_location)>=qty):
					# shop has some inventory and needs to be decremented
					cursor.execute('''INSERT INTO productmovement (timestamp,from_location,to_location,product_id,qty) values (%s,%s,%s,%s,%s)''',(timestamp,from_location,to_location,product_id,qty))
					cnx.commit()
					flash("Update successful!",'success')
				else:
					# shop doesnt have the product in inventory and need an error has to be sent
					flash("Insufficient product quantity at source!",'error')

			# Case 2
			elif(is_empty(from_location)):
				# moving item to a location, need to get the latest product qty. Insert new qty+=1 for that location and product
				# source dest is empty, so ust need to add the movement entry.
				cursor.execute('''INSERT INTO productmovement (timestamp,from_location,to_location,product_id,qty) values (%s,%s,%s,%s,%s)''',(timestamp,from_location,to_location,product_id,qty))
				cnx.commit()
				print(qty_at_loc(product_id,to_location))
				flash("Update successful!",'success')

			# Case 3
				# Search for product's quantity at src location
				# if src doesnt have a qty, return err
				# use one insert statement to descrement value from src
				# use another insert statement to increment value from src to dest
				# return success message
			else:
				srcqty = qty_at_loc(product_id,from_location)
				if(srcqty>=qty):
					cursor.execute('''INSERT INTO productmovement (timestamp,from_location,to_location,product_id,qty) values (%s,%s,%s,%s,%s)''',(timestamp,from_location,to_location,product_id,qty))
					cnx.commit()
					flash("Update successful!",'success')
				else:
					flash("Product not availabe at Source location",'error')
					return redirect(url_for('movements'))

		# return redirect(url_for('movements'))

		except mysql.connector.Error as err: 
			print("Something went wrong: {}".format(err))
			flash("Something went wrong",'error')
			return redirect(url_for('movements'))
		except:
			msg = "Select atleast one location."
			print(msg)
			flash(msg,'error')
			return redirect(url_for('movements'))

	try:
		# get list of products
		cursor.execute('''SELECT * from product''')
		products = cursor.fetchall()
		#get list of locations
		cursor.execute('''SELECT * from location''')
		locations = cursor.fetchall()
		#get list of movements
		cursor.execute('''SELECT * from productmovement''')
		movements = cursor.fetchall()
		return render_template('movements.html',movements=movements,products=products,locations=locations,qty_at_loc=qty_at_loc)
	except mysql.connector.Error as err: 
		print("Something went wrong: {}".format(err))
		flash("Something went wrong",'error')
		return redirect(url_for('movements'))



@app.route('/reports')
def reports():
	# first we will fetch all the products and locations, then for each location and each product fetch the qty of the prod.
	# Create a map and store values in that dict for each location and pass the value to the page to render.
	cursor.execute('''SELECT * from product''')
	products = cursor.fetchall()
	cursor.execute('''SELECT * from location''')
	locations = cursor.fetchall()
	return render_template('reports.html',products=products,locations = locations,qty_at_loc = qty_at_loc)

@app.route('/movements/<movement_id>/edit',methods=['GET','POST'])
def movements_edit(movement_id):
	if request.method == 'POST':
		try:
			from_location = request.form['from_location']
			to_location = request.form['to_location']
			qty = int(request.form['qty'])
			product_id = request.form['product_id']
			timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			print("heel")
			if(qty<=0):
				flash("Enter a positive quantity",'error')
				return redirect(url_for("movements_edit",movement_id=movement_id))
			if(is_empty(product_id)):
				flash("Select a product",'error')
				return redirect(url_for("movements_edit",movement_id=movement_id))

			assert(not is_empty(from_location) or not is_empty(to_location))
			# when editing, check if from_locatoin has the product quantity specified at its location first.
			if(not is_empty(from_location)):
				# if location is not empty then check whether the new qty is present at the from_location
				if(qty_at_loc(product_id,from_location,movement_id)<qty):
					flash(from_location+" only has "+ str(qty_at_loc(product_id,from_location,movement_id)) +" at source location.",'error')
					return redirect(url_for('movements_edit',movement_id=movement_id))
			cursor.execute('''update productmovement set  timestamp = %s,from_location = %s, to_location = %s, qty = %s, product_id = %s where movement_id = %s''',(timestamp,from_location,to_location,qty,product_id,movement_id))
			cnx.commit()
			flash("Edited successfully.",'success')
			return redirect(url_for('movements'))

		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
			flash("Something went wrong",'error')

		# except:
		# 	msg = "Select atleast one location."
		# 	print(msg)
		# 	flash(msg,'error')
		# 	return redirect(url_for('movements_edit',movement_id=movement_id))


	cursor.execute('''SELECT * from product''')
	products = cursor.fetchall()
	cursor.execute('''SELECT * from location''')
	locations = cursor.fetchall()
	cursor.execute('''select * from productmovement where movement_id=%s''',(movement_id,))
	movements = cursor.fetchall()
	return render_template('movements_edit.html',movements=movements,products = products, locations = locations)

@app.route('/movements/<movement_id>/delete')
def movements_delete(movement_id):
	try:
		cursor.execute('''delete from productmovement where movement_id=%s''',(movement_id,))
		cnx.commit()
		flash("Entry deleted successfully!",'success')
		return redirect(url_for('movements'))
	except mysql.connector.Error as err: 
		print("Something went wrong: {}".format(err))
		flash("Something went wrong",'error')
		return redirect(url_for('movements_edit',product_id=product_id))


if __name__ == '__main__':
    app.run()