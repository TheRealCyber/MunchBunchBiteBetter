import sqlite3
import hashlib
import datetime
import re
import os
from getpass import getpass
import cv2
from pyzbar import pyzbar
from pyNutriScore import NutriScore
from flask import Flask, render_template, request, redirect, session, url_for,jsonify,flash
import cv2
import numpy as np
import pandas as pd
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your_secret_key' 
# Paths to the databases
DB_PATH = os.path.join(os.path.dirname(__file__), 'user_auth.db')
PRODUCT_DB_PATH = os.path.join(os.path.dirname(__file__), 'product_information.db')
HEALTH_DB_PATH = os.path.join(os.path.dirname(__file__), 'health_form.db')
SHOP_DB_PATH = os.path.join(os.path.dirname(__file__), 'shopping_list.db')
FAV_DB_PATH = os.path.join(os.path.dirname(__file__), 'fav_list.db')
REC_PRODUCT_PATH=os.path.join(os.path.dirname(__file__), 'rec_file.csv')

def add_to_shopping_list(username, product, quantity_shop):
    conn = sqlite3.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    try:
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shopping_list (
            username TEXT,
            id INTEGER,
            barcode_num TEXT PRIMARY KEY,
            product_name TEXT,
            ingredients TEXT,
            energy REAL,
            proteins REAL,
            carbohydrates REAL,
            cholesterol REAL,
            sugars REAL,
            total_fat REAL,
            saturated_fat REAL,
            trans_fat REAL,
            sodium REAL,
            fruits_vegetables_nuts REAL,
            dietary_fibre REAL DEFAULT 0,
            allergens TEXT,
            nutrition_grade TEXT,
            calcium REAL DEFAULT 0,
            iodine REAL DEFAULT 0,
            zinc REAL DEFAULT 0,
            phosphorous REAL DEFAULT 0,
            magnesium REAL DEFAULT 0,
            vitamin_A REAL DEFAULT 0,
            vitamin_B REAL DEFAULT 0,
            vitamin_C REAL DEFAULT 0,
            vitamin_D REAL DEFAULT 0,
            vitamin_E REAL DEFAULT 0,
            vitamin_K REAL DEFAULT 0,
            other TEXT DEFAULT "",
            quantity_shop INT
            )
        ''')
        
        # Ensure quantity_shop is an integer
        quantity_shop = int(quantity_shop)
        
        # Check if the product with the same barcode already exists
        cursor.execute('SELECT quantity_shop FROM shopping_list WHERE barcode_num = ?', (product[1],))
        existing_record = cursor.fetchone()
        
        if existing_record:
            # If barcode exists, update the quantity
            new_quantity = existing_record[0] + quantity_shop
            cursor.execute('UPDATE shopping_list SET quantity_shop = ? WHERE barcode_num = ?', (new_quantity, product[1]))
            print(f'Updated quantity for product "{product[2]}" to {new_quantity}.')
        else:
            # If barcode doesn't exist, insert a new record
            product_data = product + (quantity_shop,)
            cursor.execute('''
                INSERT INTO shopping_list (username, id, barcode_num, product_name, ingredients, energy, proteins, carbohydrates, cholesterol, sugars, total_fat, saturated_fat,
                                          trans_fat, sodium, fruits_vegetables_nuts, dietary_fibre, allergens, nutrition_grade, calcium, iodine, zinc, phosphorous, magnesium, vitamin_A, vitamin_B, vitamin_C, vitamin_D, vitamin_E, vitamin_K, other, quantity_shop)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username,) + product_data)
            print(f'Product "{product[2]}" added to shopping list with quantity {quantity_shop}.')
        
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()




# @app.route('/add_to_shopping_list', methods=['GET', 'POST'])
# def add_to_shopping_list_view():
#     if request.method == 'POST':
#         if 'username' not in session:
#             flash('You need to log in to add products to the shopping list.', 'danger')
#             return redirect(url_for('login'))

#         username = session['username']
#         barcode = request.form.get('barcode')
#         quantity = request.form.get('quantity')

#         product = get_product_info(barcode)  # Ensure this function works correctly

#         if product:
#             add_to_shopping_list(username, product, quantity)
#             flash('Product successfully added to the shopping list.', 'success')
#         else:
#             flash(f"No product found with barcode {barcode}", 'danger')

#         return redirect(url_for('shopping_list'))  # Redirect to the shopping list

#     return render_template('shopping_list.html')  # Handle GET request



@app.route('/add_to_shopping_list', methods=['GET', 'POST'])
def add_to_shopping_list_view():
    if request.method == 'POST':
        if 'username' not in session:
            flash('You need to log in to add products to the shopping list.', 'danger')
            return redirect(url_for('login'))

        username = session['username']
        barcode = request.form.get('barcode')
        quantity = request.form.get('quantity')

        product = get_product_info(barcode)  # Ensure this function works correctly

        if product:
            add_to_shopping_list(username, product, quantity)
            flash('Product successfully added to the shopping list.', 'success')
        else:
            flash(f"No product found with barcode {barcode}", 'danger')

        return redirect(url_for('shopping_list'))  # Redirect to the shopping list

    return render_template('shopping_list.html')  # Handle GET request




# Function to fetch product info by barcode (you already have this)
def get_product_info(barcode):
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT id, barcode_num, product_name, ingredients, energy, proteins, carbohydrates, cholesterol, sugars, total_fat, saturated_fat,
                    trans_fat, sodium, fruits_vegetables_nuts, dietary_fibre, allergens, nutrition_grade, calcium, iodine, zinc, phosphorous, magnesium,
                    vitamin_A, vitamin_B, vitamin_C, vitamin_D, vitamin_E, vitamin_K, other
            FROM products WHERE barcode_num = ?
        ''', (barcode,))
        result = cursor.fetchone()
        return result
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
    return None




def add_to_fav_list(username, product):
    conn = sqlite3.connect(FAV_DB_PATH)
    cursor = conn.cursor()
    try:
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fav_list (
            username TEXT,
            id INTEGER,
            barcode_num TEXT PRIMARY KEY,
            product_name TEXT,
            ingredients TEXT,
            energy REAL,
            proteins REAL,
            carbohydrates REAL,
            cholesterol REAL,
            sugars REAL,
            total_fat REAL,
            saturated_fat REAL,
            trans_fat REAL,
            sodium REAL,
            fruits_vegetables_nuts REAL,
            dietary_fibre REAL DEFAULT 0,
            allergens TEXT,
            nutrition_grade TEXT,
            calcium REAL DEFAULT 0,
            iodine REAL DEFAULT 0,
            zinc REAL DEFAULT 0,
            phosphorous REAL DEFAULT 0,
            magnesium REAL DEFAULT 0,
            vitamin_A REAL DEFAULT 0,
            vitamin_B REAL DEFAULT 0,
            vitamin_C REAL DEFAULT 0,
            vitamin_D REAL DEFAULT 0,
            vitamin_E REAL DEFAULT 0,
            vitamin_K REAL DEFAULT 0,
            other TEXT DEFAULT "",
            quantity_favourite INT DEFAULT 1  -- Kept but not used
            )
        ''')
        
        # Check if the product with the same barcode already exists
        cursor.execute('SELECT 1 FROM fav_list WHERE barcode_num = ?', (product[1],))
        existing_record = cursor.fetchone()
        
        if not existing_record:
            # If barcode doesn't exist, insert a new record
            cursor.execute('''
                INSERT INTO fav_list (username, id, barcode_num, product_name, ingredients, energy, proteins, carbohydrates, cholesterol, sugars, total_fat, saturated_fat,
                                          trans_fat, sodium, fruits_vegetables_nuts, dietary_fibre, allergens, nutrition_grade, calcium, iodine, zinc, phosphorous, magnesium, vitamin_A, vitamin_B, vitamin_C, vitamin_D, vitamin_E, vitamin_K, other)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username,) + product)
            print(f'Product "{product[2]}" added to fav list.')
        
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()






@app.route('/add_to_favorite', methods=['GET', 'POST'])
def add_to_favorite():
    if request.method == 'POST':
        if 'username' not in session:
            flash('You need to log in to add favorites.', 'danger')
            return redirect(url_for('login'))

        username = session['username']  # Get the username from the session
        barcode = request.form['barcode']
        
        product = get_product_info(barcode)  # Fetch product details
        
        if product:
            add_to_fav_list(username, product)
            flash('Product added to favorites successfully!', 'success')
        else:
            flash(f'No product found with barcode {barcode}', 'danger')

        return redirect(url_for('fav_list'))

    return render_template('add_to_favorite.html')


def view_fav_list(username):

    conn = sqlite3.connect(FAV_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM fav_list WHERE username=?', (username,))
        products = cursor.fetchall()
        if products:
            print("\nFavourite List:")
            for item in products:
                print(f"- Product Name: {item[3]} , Quantity: {item[30]} ")
        else:
            print("Your favourite list is empty.")
    except sqlite3.Error as e:
            print(f"An error occurred: {e}. It might be caused by an invalid column name or unexpected characters.")
    finally:
        conn.close() 



@app.route('/fav_list', methods=['GET'])
def fav_list():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not authenticated

    username = session['username']

    conn = sqlite3.connect(FAV_DB_PATH)
    cursor = conn.cursor()
    try:
        # Only fetch product details, excluding the username
        cursor.execute('SELECT barcode_num, product_name, quantity_favourite FROM fav_list WHERE username=?', (username,))
        products = cursor.fetchall()
        return render_template('fav_list.html', products=products)
    except sqlite3.Error as e:
        return f"An error occurred: {e}. It might be caused by an invalid column name or unexpected characters."
    finally:
        conn.close()


# def view_shopping_list(username):
#     conn = sqlite3.connect(SHOP_DB_PATH)
#     cursor = conn.cursor()
#     try:
#         cursor.execute('SELECT * FROM shopping_list WHERE username=?', (username,))
#         products = cursor.fetchall()
#         if products:
#             print("\nShopping List:")
#             for item in products:
#                 print(f"- Product Name: {item[3]} , Quantity: {item[30]} ")
#         else:
#             print("Your shopping list is empty.")
#     except sqlite3.Error as e:
#             print(f"An error occurred: {e}. It might be caused by an invalid column name or unexpected characters.")
#     finally:
#         conn.close()


# @app.route('/shopping_list', methods=['GET'])
# def shopping_list():
#     if 'username' not in session:
#         return redirect(url_for('login'))  # Redirect to login if user is not authenticated

#     username = session['username']

#     with sqlite3.connect(SHOP_DB_PATH) as conn:
#         cursor = conn.cursor()
#         try:
#             cursor.execute('SELECT * FROM shopping_list WHERE username=?', (username,))
#             products = cursor.fetchall()
#             return render_template('view_shopping_list.html', products=products)
#         except sqlite3.Error as e:
#             return f"An error occurred: {e}. It might be caused by an invalid column name or unexpected characters."

def view_shopping_list(username):
    conn = sqlite3.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM shopping_list WHERE username=?', (username,))
        products = cursor.fetchall()
        if products:
            print("\nShopping List:")
            for item in products:
                print(f"- Product Name: {item[3]} , Quantity: {item[30]}")
            
            # Call the classify shopping cart feature
            cart_classification = classify_shopping_cart(username)
            if cart_classification:
                print("\nShopping Cart Classification:")
                for product, classification in cart_classification.items():
                    print(f"- {product}: {classification}")
            else:
                print("\nUnable to classify the shopping cart. Ensure valid product data exists.")
        else:
            print("Your shopping list is empty.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}. It might be caused by an invalid column name or unexpected characters.")
    finally:
        conn.close()

def classify_shopping_cart(username):
    """
    Classifies products in the shopping cart based on health scoring or other criteria.

    Args:
        username (str): Username of the person whose cart is being classified.

    Returns:
        dict: Dictionary with product names as keys and classification (e.g., Healthy, Average, Unhealthy) as values.
    """
    conn = sqlite3.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT product_name, energy, proteins, sugars, total_fat FROM shopping_list WHERE username=?', (username,))
        products = cursor.fetchall()
        classifications = {}

        # Apply classification logic for each product
        for product in products:
            product_name, energy, proteins, sugars, total_fat = product
            if energy < 150 and sugars < 5 and proteins > 10:
                classifications[product_name] = 'Goal Friendly'
            elif sugars > 15 or total_fat > 20:
                classifications[product_name] = 'Goal Unfriendly'
            else:
                classifications[product_name] = 'Goal Friendly'
        return classifications
    except sqlite3.Error as e:
        print(f"An error occurred while classifying the cart: {e}")
        return {}
    finally:
        conn.close()
        
# @app.route('/shopping_list', methods=['GET'])
# def shopping_list():
#     # Check if the user is logged in
#     if 'username' not in session:
#         return redirect(url_for('login'))  # Redirect to login if user is not authenticated

#     username = session['username']

#     try:
#         # Connect to the database
#         with sqlite3.connect(SHOP_DB_PATH) as conn:
#             cursor = conn.cursor()
#             cursor.execute('SELECT * FROM shopping_list WHERE username=?', (username,))
#             products = cursor.fetchall()

#             # If products exist, display them
#             if products:
#                 # Process products for rendering in the view
#                 cart_classification = classify_shopping_cart(username)
#                 return render_template('view_shopping_list.html', products=products, classifications=cart_classification)

#             else:
#                 return "Your shopping list is empty."

#     except sqlite3.Error as e:
#         return f"An error occurred: {e}. It might be caused by an invalid column name or unexpected characters."



@app.route('/shopping_list', methods=['GET'])
def shopping_list():
    # Check if the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not authenticated

    username = session['username']

    try:
        # Connect to the database
        with sqlite3.connect(SHOP_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM shopping_list WHERE username=?', (username,))
            products = cursor.fetchall()

            # If products exist, process them and classify
            if products:
                goal_friendly_products = []
                goal_unfriendly_products = []

                # Assuming the classify_shopping_cart function classifies each product in the cart
                cart_classification = classify_shopping_cart(username)

                # Classify products into goal-friendly and goal-unfriendly
                for item in products:
                    product_name = item[3]
                    classification = cart_classification.get(product_name, 'Unknown')
                    
                    if classification == 'Goal Friendly':
                        goal_friendly_products.append(item)
                    elif classification == 'Goal Unfriendly':
                        goal_unfriendly_products.append(item)
                    else:
                        goal_unfriendly_products.append(item)  # Default to "Unfriendly" if unknown

                # Render template with classified products
                return render_template('view_shopping_list.html', 
                                       goal_friendly_products=goal_friendly_products, 
                                       goal_unfriendly_products=goal_unfriendly_products)

            else:
                 return render_template('no_shopping.html')

    except sqlite3.Error as e:
        return f"An error occurred: {e}. It might be caused by an invalid column name or unexpected characters."


def delete_from_fav_list(username, product_name_fav):
    conn = sqlite3.connect(FAV_DB_PATH)
    cursor = conn.cursor()
    try:
        # Attempt to delete the product directly by product name and username
        cursor.execute('''
            DELETE FROM fav_list 
            WHERE username = ? AND product_name = ?
        ''', (username, product_name_fav))
        
        conn.commit()
        print(f'Removed product "{product_name_fav}" from the favourite list.')

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        
@app.route('/delete_from_fav', methods=['POST'])
def delete_from_fav():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if the user is not authenticated

    username = session['username']
    product_name_fav = request.form.get('product_name')

    try:
        delete_from_fav_list(username, product_name_fav)  # Call the updated function
        flash(f'Product "{product_name_fav}" removed from the favourite list.', 'success')
    except Exception as e:
        flash(f"An error occurred: {e}", 'danger')
    
    return redirect(url_for('fav_list'))  # Redirect back to the favourite list page




def delete_from_shopping_list(username, product_name, quantity_to_delete_shop):
    conn = sqlite3.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    try:
        # First, check if the product exists by product name
        cursor.execute('''
            SELECT product_name, quantity_shop 
            FROM shopping_list 
            WHERE username = ? AND product_name = ?
        ''', (username, product_name))
        
        product = cursor.fetchone()
        
        if product:
            current_quantity = product[1]  # Get the current quantity (second column is quantity_shop)
            new_quantity = current_quantity - int(quantity_to_delete_shop)  # Ensure quantity_to_delete_shop_shop is an integer
            
            if new_quantity > 0:
                # Update the quantity in the database if the new quantity is greater than zero
                cursor.execute('''
                    UPDATE shopping_list 
                    SET quantity_shop = ? 
                    WHERE username = ? AND product_name = ?
                ''', (new_quantity, username, product_name))  # Use only product_name for the update
                print(f'Updated quantity for product "{product[0]}" to {new_quantity}.')
            else:
                # If new quantity is 0 or less, remove the product from the list
                cursor.execute('''
                    DELETE FROM shopping_list 
                    WHERE username = ? AND product_name = ?
                ''', (username, product_name))  # Use only product_name for the deletion
                print(f'Removed product "{product[0]}" from the shopping list.')
                
            conn.commit()
        else:
            print(f'Product "{product_name}" not found in the shopping list.')

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# @app.route('/delete_from_shop', methods=['POST'])
# def delete_from_shop():
#     if 'username' not in session:
#         return redirect(url_for('login'))  # Redirect to login if user is not authenticated

#     username = session['username']
#     product_name = request.form.get('product_name')
#     quantity_to_delete_shop = request.form.get('quantity_to_delete')

#     conn = sqlite3.connect(SHOP_DB_PATH)
#     cursor = conn.cursor()
#     try:
#         cursor.execute('''
#             SELECT product_name, quantity_shop
#             FROM shopping_list
#             WHERE username = ? AND product_name = ?
#         ''', (username, product_name))
        
#         product = cursor.fetchone()
        
#         if product:
#             current_quantity = product[1]
#             new_quantity = current_quantity - int(quantity_to_delete_shop)
            
#             if new_quantity > 0:
#                 cursor.execute('''
#                     UPDATE shopping_list
#                     SET quantity_shop = ?
#                     WHERE username = ? AND product_name = ?
#                 ''', (new_quantity, username, product_name))
#                 message = f'Updated quantity for product "{product[0]}" to {new_quantity}.'
#             else:
#                 cursor.execute('''
#                     DELETE FROM shopping_list
#                     WHERE username = ? AND product_name = ?
#                 ''', (username, product_name))
#                 message = f'Removed product "{product[0]}" from the shopping list.'
                
#             conn.commit()
#         else:
#             message = f'Product "{product_name}" not found in the shopping list.'

#     except sqlite3.Error as e:
#         message = f"An error occurred: {e}"
#     finally:
#         conn.close()
    
#     return redirect(url_for('shopping_list'))  # Redirect back to the shopping list page with a message

@app.route('/delete_from_shop', methods=['POST'])
def delete_from_shop():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not authenticated

    username = session['username']
    product_name = request.form.get('product_name')

    try:
        quantity_to_delete_shop = int(request.form.get('quantity_to_delete'))
        if quantity_to_delete_shop <= 0:
            flash("Quantity to delete must be a positive number.")
            return redirect(url_for('shopping_list'))
    except (ValueError, TypeError):
        flash("Invalid quantity provided.")
        return redirect(url_for('shopping_list'))

    with sqlite3.connect(SHOP_DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT product_name, quantity_shop
                FROM shopping_list
                WHERE username = ? AND product_name = ?
            ''', (username, product_name))
            
            product = cursor.fetchone()
            
            if product:
                current_quantity = product[1]
                new_quantity = current_quantity - quantity_to_delete_shop
                
                if new_quantity > 0:
                    cursor.execute('''
                        UPDATE shopping_list
                        SET quantity_shop = ?
                        WHERE username = ? AND product_name = ?
                    ''', (new_quantity, username, product_name))
                    message = f'Updated quantity for product "{product[0]}" to {new_quantity}.'
                else:
                    cursor.execute('''
                        DELETE FROM shopping_list
                        WHERE username = ? AND product_name = ?
                    ''', (username, product_name))
                    message = f'Removed product "{product[0]}" from the shopping list.'
                    
                conn.commit()
            else:
                message = f'Product "{product_name}" not found in the shopping list.'

        except sqlite3.Error as e:
            message = f"An error occurred: {e}"
        
        flash(message)
    
    return redirect(url_for('shopping_list'))



def calculate_nutrition_summary_fav():
    conn = sqlite3.connect(FAV_DB_PATH)
    cursor = conn.cursor()
    total_carbohydrates = 0
    total_proteins = 0
    total_sugars = 0
    total_fat = 0
    total_sodium = 0

    try:
        cursor.execute('SELECT carbohydrates, proteins, sugars, total_fat, sodium FROM fav_list')
        products = cursor.fetchall()
        
        for product in products:
            total_carbohydrates += product[0] if product[0] is not None else 0
            total_proteins += product[1] if product[1] is not None else 0
            total_sugars += product[2] if product[2] is not None else 0
            total_fat += product[3] if product[3] is not None else 0
            total_sodium += product[4] if product[4] is not None else 0
        
        print("\nNutrition Summary of Favourite List:")
        print(f"Total Carbohydrates: {total_carbohydrates:.2f} g")
        print(f"Total Proteins: {total_proteins:.2f} g")
        print(f"Total Sugars: {total_sugars:.2f} g")
        print(f"Total Fat: {total_fat:.2f} g")
        print(f"Total Sodium: {total_sodium:.2f} g")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def calculate_nutrition_summary_shopping():
    conn = sqlite3.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    total_carbohydrates = 0
    total_proteins = 0
    total_sugars = 0
    total_fat = 0
    total_sodium = 0

    try:
        cursor.execute('SELECT carbohydrates, proteins, sugars, total_fat, sodium FROM shopping_list')
        products = cursor.fetchall()
        
        for product in products:
            total_carbohydrates += product[0] if product[0] is not None else 0
            total_proteins += product[1] if product[1] is not None else 0
            total_sugars += product[2] if product[2] is not None else 0
            total_fat += product[3] if product[3] is not None else 0
            total_sodium += product[4] if product[4] is not None else 0
        
        print("\nNutrition Summary of Shopping List:")
        print(f"Total Carbohydrates: {total_carbohydrates:.2f} g")
        print(f"Total Proteins: {total_proteins:.2f} g")
        print(f"Total Sugars: {total_sugars:.2f} g")
        print(f"Total Fat: {total_fat:.2f} g")
        print(f"Total Sodium: {total_sodium:.2f} g")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# @app.route('/nutrition_summary_fav')
# def nutrition_summary_fav():
#     if 'username' not in session:
#         return redirect(url_for('login'))  # Redirect to login if user is not authenticated

#     conn = sqlite3.connect(FAV_DB_PATH)
#     cursor = conn.cursor()
#     total_carbohydrates = 0
#     total_proteins = 0
#     total_sugars = 0
#     total_fat = 0
#     total_sodium = 0

#     try:
#         cursor.execute('SELECT carbohydrates, proteins, sugars, total_fat, sodium FROM fav_list')
#         products = cursor.fetchall()

#         for product in products:
#             total_carbohydrates += product[0] if product[0] is not None else 0
#             total_proteins += product[1] if product[1] is not None else 0
#             total_sugars += product[2] if product[2] is not None else 0
#             total_fat += product[3] if product[3] is not None else 0
#             total_sodium += product[4] if product[4] is not None else 0

#     except sqlite3.Error as e:
#         return f"An error occurred: {e}"
#     finally:
#         conn.close()

#     return render_template('nutrition_summary_fav.html', total_carbohydrates=total_carbohydrates,
#                            total_proteins=total_proteins, total_sugars=total_sugars,
#                            total_fat=total_fat, total_sodium=total_sodium)


@app.route('/nutrition_summary_fav')
def nutrition_summary_fav():
    if 'username' not in session:
        return redirect(url_for('login'))  

    username = session['username']  

    conn = sqlite3.connect(FAV_DB_PATH)
    cursor = conn.cursor()
    total_carbohydrates = 0
    total_proteins = 0
    total_sugars = 0
    total_fat = 0
    total_sodium = 0

    try:
      
        cursor.execute('SELECT carbohydrates, proteins, sugars, total_fat, sodium FROM fav_list WHERE username=?', (username,))
        products = cursor.fetchall()

        for product in products:
            total_carbohydrates += product[0] if product[0] is not None else 0
            total_proteins += product[1] if product[1] is not None else 0
            total_sugars += product[2] if product[2] is not None else 0
            total_fat += product[3] if product[3] is not None else 0
            total_sodium += product[4] if product[4] is not None else 0

    except sqlite3.Error as e:
        return f"An error occurred: {e}"
    finally:
        conn.close()

    return render_template('nutrition_summary_fav.html', total_carbohydrates=total_carbohydrates,
                           total_proteins=total_proteins, total_sugars=total_sugars,
                           total_fat=total_fat, total_sodium=total_sodium)



@app.route('/nutrition_summary_shop')
def nutrition_summary_shop():
    if 'username' not in session:
        return redirect(url_for('login')) 

    username = session['username']  

    conn = sqlite3.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    total_carbohydrates = 0
    total_proteins = 0
    total_sugars = 0
    total_fat = 0
    total_sodium = 0

    try:
       
        cursor.execute('SELECT carbohydrates, proteins, sugars, total_fat, sodium FROM shopping_list WHERE username=?', (username,))
        products = cursor.fetchall()

        for product in products:
            total_carbohydrates += product[0] if product[0] is not None else 0
            total_proteins += product[1] if product[1] is not None else 0
            total_sugars += product[2] if product[2] is not None else 0
            total_fat += product[3] if product[3] is not None else 0
            total_sodium += product[4] if product[4] is not None else 0

    except sqlite3.Error as e:
        return f"An error occurred: {e}"
    finally:
        conn.close()

    return render_template('nutrition_summary_shop.html', total_carbohydrates=total_carbohydrates,
                           total_proteins=total_proteins, total_sugars=total_sugars,
                           total_fat=total_fat, total_sodium=total_sodium)



# @app.route('/nutrition_summary_shop')
# def nutrition_summary_shop():
#     if 'username' not in session:
#         return redirect(url_for('login'))  # Redirect to login if user is not authenticated

#     conn = sqlite3.connect(SHOP_DB_PATH)
#     cursor = conn.cursor()
#     total_carbohydrates = 0
#     total_proteins = 0
#     total_sugars = 0
#     total_fat = 0
#     total_sodium = 0

#     try:
#         cursor.execute('SELECT carbohydrates, proteins, sugars, total_fat, sodium FROM shopping_list')
#         products = cursor.fetchall()

#         for product in products:
#             total_carbohydrates += product[0] if product[0] is not None else 0
#             total_proteins += product[1] if product[1] is not None else 0
#             total_sugars += product[2] if product[2] is not None else 0
#             total_fat += product[3] if product[3] is not None else 0
#             total_sodium += product[4] if product[4] is not None else 0

#     except sqlite3.Error as e:
#         return f"An error occurred: {e}"
#     finally:
#         conn.close()

#     return render_template('nutrition_summary_shop.html', total_carbohydrates=total_carbohydrates,
#                            total_proteins=total_proteins, total_sugars=total_sugars,
#                            total_fat=total_fat, total_sodium=total_sodium)


def preprocess_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresholded = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return thresholded

def read_barcodes(frame):
    try:
        barcodes = pyzbar.decode(frame)
        for barcode in barcodes:
            barcode_info = barcode.data.decode('utf-8')
            if barcode_info.isdigit():
                return barcode_info
    except Exception as e:
        print(f"Error decoding barcode: {e}")
    return None

def scan_barcode(username, stream_url=None):
    if stream_url is None:
        # Get user input for the IP address
        ip_address = input("Enter the IP address of your phone (e.g., 192.168.1.100): ")
        stream_url = f'http://{ip_address}:8080/video'

    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    print("Scanning barcode... Press 'q' to quit.")
    scanned_barcodes = set()  # Keep track of scanned barcodes to avoid duplicates

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Process the frame and read the barcode
        processed_frame = preprocess_frame(frame)
        barcode = read_barcodes(processed_frame)

        if barcode and barcode not in scanned_barcodes:
            scanned_barcodes.add(barcode)
            print(f"\nBarcode detected: {barcode}")
            display_product_info(username, barcode)  # Pass the barcode directly to display_product_info

        cv2.imshow('Barcode Scanner', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Scanning cancelled by user")
            break

    cap.release()
    cv2.destroyAllWindows()

def get_product_info(barcode):
    # Connect to the SQLite database
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()
    try:
        # Query to fetch all columns for the matching barcode
        query = """
        SELECT id, barcode_num, product_name, ingredients, energy, proteins, carbohydrates, cholesterol, sugars, total_fat, saturated_fat,
                                       trans_fat, sodium, fruits_vegetables_nuts, dietary_fibre, allergens, nutrition_grade, calcium, iodine, zinc, phosphorous, magnesium, vitamin_A, vitamin_B, vitamin_C, vitamin_D, vitamin_E, vitamin_K, other
        FROM products
        WHERE barcode_num = ?
        """
        # Execute the query with the scanned barcode
        cursor.execute(query, (barcode,))
        # Fetch the result
        result = cursor.fetchone()
        return result
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the database connection
        conn.close()
    return None



# Preprocess frame for better barcode scanning
def preprocess_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresholded = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return thresholded

# Read barcodes from a video frame
def read_barcodes(frame):
    try:
        barcodes = pyzbar.decode(frame)
        for barcode in barcodes:
            barcode_info = barcode.data.decode('utf-8')
            if barcode_info.isdigit():
                return barcode_info
    except Exception as e:
        print(f"Error decoding barcode: {e}")
    return None

# Scan barcode functionality with custom IP address
@app.route('/scan_barcode', methods=['GET', 'POST'])
def scan_barcode_route():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    if request.method == 'POST':
        ip_address = request.form.get('ip_address')
        stream_url = f'http://{ip_address}:8080/video'

        # Start barcode scanning
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            return jsonify({"error": "Error: Could not open video stream."})

        scanned_barcodes = set()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            processed_frame = preprocess_frame(frame)
            barcode = read_barcodes(processed_frame)

            if barcode and barcode not in scanned_barcodes:
                scanned_barcodes.add(barcode)
                product_info = get_product_info(barcode)
                if product_info:
                    return render_template('product_info.html', product=product_info)
                    # return jsonify(product_info)

            cv2.imshow('Barcode Scanner', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    return render_template('scan_barcode.html')

# @app.route('/input_barcode', methods=['GET', 'POST'])
# def input_barcode():
#     if 'username' not in session:
#         return redirect(url_for('login'))
    
#     username = session['username']

#     if request.method == 'POST':
#         barcode_num = request.form.get('barcode_num')

#         # Fetch product info using the input barcode number
#         product_info = get_product_info(barcode_num)

#         if product_info:
#             # Render the product details page with the product info
#             return render_template('product_info.html', product=product_info)
#         else:
#             # If no product is found, show an error message
#             error_message = "No product found for this barcode."
#             return render_template('input_barcode.html', error=error_message)

#     return render_template('input_barcode.html')



# Fetch product information from the database using the barcode
def get_product_info(barcode):
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()
    try:
        query = """
        SELECT id, barcode_num, product_name, ingredients, energy, proteins, carbohydrates, cholesterol, sugars, total_fat, 
               saturated_fat, trans_fat, sodium, fruits_vegetables_nuts, dietary_fibre, allergens, nutrition_grade, calcium, iodine, zinc, phosphorous, magnesium, vitamin_A, 
               vitamin_B, vitamin_C, vitamin_D, vitamin_E, vitamin_K, other
        FROM products
        WHERE barcode_num = ?
        """
        cursor.execute(query, (barcode,))
        result = cursor.fetchone()
        return result if result else None
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
    return None



def display_product_info(username, barcode):
    result = get_product_info(barcode)
    if result:
        # Display the product information
        print("\nProduct Information:")
        print(f"ID: {result[0]}")
        print(f"Barcode: {result[1]}")
        print(f"Product Name: {result[2]}")
        print(f"Ingredients: {result[3]}")
        print(f"Energy: {result[4]} kcal")
        print(f"Proteins: {result[5]} g")
        print(f"Carbohydrates: {result[6]} g")
        print(f"Cholesterol: {result[7]} g")
        print(f"Sugars: {result[8]} g")
        print(f"Total Fat: {result[9]} g")
        print(f"Saturated Fat: {result[10]} g")
        print(f"Trans Fat: {result[11]} g")
        print(f"Sodium: {result[12]} g")
        print(f"Fruits/Vegetables/Nuts: {result[13]} g")
        print(f"Dietary fibre: {result[14]} g")
        print(f"Allergens: {result[15]}")
        print(f"Nutrition Grade: {result[16]}")

        # Only display these values if they are not 0
        if result[17] != 0:
            print(f"Calcium: {result[17]} g")
        if result[18] != 0:
            print(f"Iodine: {result[18]} g")
        if result[19] != 0:
            print(f"Zinc: {result[19]} g")
        if result[20] != 0:
            print(f"Phosphorous: {result[20]} g")
        if result[21] != 0:
            print(f"Magnesium: {result[21]} g")
        if result[22] != 0:
            print(f"Vitamin A: {result[22]} g")
        if result[23] != 0:
            print(f"Vitamin B: {result[23]} g")
        if result[24] != 0:
            print(f"Vitamin C: {result[24]} g")
        if result[25] != 0:
            print(f"Vitamin D: {result[25]} g")
        if result[26] != 0:
            print(f"Vitamin E: {result[26]} g")
        if result[27] != 0:
            print(f"Vitamin K: {result[27]} g")
        if result[28]:  # Assuming 'other' is a string and we want to display it if it's not empty
            print(f"Other: {result[28]}")

        # Rest of the function remains the same
        allergens = result[15]  # Assuming this is a list of allergens
        if 'milk' in allergens.lower():
            print("\n⚠️ WARNING: This product contains dairy!")
        if 'wheat' in allergens.lower():
            print("\n⚠️ WARNING: This product contains wheat!")
        if 'soy' in allergens.lower():
            print("\n⚠️ WARNING: This product contains soy!")
        if 'peanut' in allergens.lower():
            print("\n⚠️ WARNING: This product contains peanut!")
        if 'nut' in allergens.lower():
            print("\n⚠️ WARNING: This product contains nuts!")
        if 'sulphite' in allergens.lower():
            print("\n⚠️ WARNING: This product contains sulphite!")

        # Nutritional tags based on specified conditions
        sugars = result[8]
        sodium = result[12]
        energy_kcal = result[4]
        fats = result[9]
        saturated_fat = result[10]
        proteins = result[5]

        if sugars > 22.5:
            print("\n⚠️ WARNING: This product is high in sugar!")
        elif sugars <= 5:
            print("\n🍎 NOTE: This product is low in sugar!")

        if sodium > 0.6:
            print("\n⚠️ WARNING: This product is high in sodium!")
        elif sodium <= 0.1:
            print("\n🥗 NOTE: This product is low in sodium!")

        if energy_kcal > 0:
            protein_energy_percentage = (proteins * 4 / energy_kcal) * 100
            if protein_energy_percentage >= 20:
                print("\n💪 NOTE: This product is high in protein!")

        if fats > 17.5:
            print("\n🍔 WARNING: This product is high in total fat!")
        elif fats < 0.5:
            print("\n🥬 NOTE: This product is fat-free!")
        elif fats < 3:
            print("\n🥗 NOTE: This product is low in fat!")

        if saturated_fat > 5:
            print("\n🥓 WARNING: This product is high in saturated fat!")
        elif saturated_fat < 0.1:
            print("\n🌱 NOTE: This product is free of saturated fat!")
        elif saturated_fat < 1.5:
            print("\n🥑 NOTE: This product is low in saturated fat!")

          # Retrieve the user's health data
        conn = sqlite3.connect(HEALTH_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM health_form WHERE username = ?", (username,))
        user_health_data = cursor.fetchone()
        conn.close()

        if user_health_data:
            # Prepare user health data for score calculation
            user_data = {
                'age': user_health_data[1],
                'height': user_health_data[2],
                'weight': user_health_data[3],
                'diet_type': user_health_data[4],
                'chronic_illnesses': user_health_data[5],
                'dietary_restrictions': user_health_data[6],
                'trigger_ingredients': user_health_data[7],
                'health_goals': user_health_data[8]
            }

            # Prepare product data for score calculation
            product_data = {
                'energy': result[4],
                'proteins': result[5],
                'carbohydrates': result[6],
                'cholesterol': result[7],
                'sugars': result[8],
                'total_fat': result[9],
                'saturated_fat': result[10],
                'trans_fat': result[11],
                'sodium': result[12],
                'dietary_fibre': result[14],
                'allergens': result[15]
            }

            # # Calculate the health score
            # health_score = calculate_health_score(user_data, product_data)
            # print(f"\n🧑‍⚕️ Health Score (for {username}): {health_score}/5")   

        # Ask if the user wants to add the product to the shopping list
        add_to_shop_list = input("\nDo you want to add this product to your shopping list? (yes/no): ").strip().lower()
        if add_to_shop_list == 'yes':
            quantity_shop = input("\n Enter quantity of product (int): ")
            add_to_shopping_list(username, result, quantity_shop)  # Pass all fields of the product

        view_shop_list = input("Do you want to view your shopping list? (yes/no): ").strip().lower()
        if view_shop_list == 'yes':
            view_shopping_list(username)

        nut_sum_shop = input("Do you want to view nutrition summary of your shopping list? (yes/no): ").strip().lower()
        if nut_sum_shop == 'yes':
            calculate_nutrition_summary_shopping()

        add_to_favorite_list = input("\nDo you want to add this product to your favourite list? (yes/no): ").strip().lower()

        if add_to_favorite_list == 'yes':
            quantity_favourite = input("\n Enter quantity of product (int): ")
            add_to_fav_list(username, result, quantity_favourite)  # Pass all fields of the product

        view_favourite_list = input("Do you want to view your favourite list? (yes/no): ").strip().lower()
        if view_favourite_list == 'yes':
            view_fav_list(username)

        nut_sum_fav = input("Do you want to view nutrition summary of your favourite list? (yes/no): ").strip().lower()
        if nut_sum_fav == 'yes':
            calculate_nutrition_summary_shopping()
    else:
        print(f"No product found with barcode: {barcode}")


# def calculate_health_score(user_health_data, product_data):
    
#     score = 50  # Start with a neutral score of 50
#     max_score = 100
    
#     # Normalize user health data
#     chronic_illnesses = [illness.strip().lower() for illness in user_health_data.get('chronic_illnesses', '').split(',')]
#     dietary_restrictions = [restriction.strip().lower() for restriction in user_health_data.get('dietary_restrictions', '').split(',')]
#     trigger_ingredients = [trigger.strip().lower() for trigger in user_health_data.get('trigger_ingredients', '').split(',')]
#     health_goals = [goal.strip().lower() for goal in user_health_data.get('health_goals', '').split(',')]

#     # Assign penalties based on chronic illnesses and allergens
#     if 'lactose intolerance' in chronic_illnesses and 'lactose' in product_data.get('allergens', '').lower():
#         score -= 10
#     if 'diabetes' in chronic_illnesses and product_data.get('sugars', 0) > 25:  # Increased sugar threshold
#         score -= 20  # Reduced sugar penalty
#     if 'high blood pressure' in chronic_illnesses and product_data.get('sodium', 0) > 200:
#         score -= 15

#     # Assign rewards for health goals and dietary preferences
#     if 'low-sugar' in dietary_restrictions and product_data.get('sugars', 0) < 10:
#         score += 10
#     if 'protein-rich' in dietary_restrictions and product_data.get('proteins', 0) > 15:
#         score += 25  # Slightly reduced reward to balance
#     if 'bodybuilding' in health_goals and product_data.get('proteins', 0) > 15:
#         score += 35  # Increased reward for protein-rich products
#     if 'fiber-rich' in dietary_restrictions and product_data.get('dietary_fibre', 0) > 8:
#         score += 10  # Reward for high fiber

#     # Penalties for unhealthy content
#     if product_data.get('sugars', 0) > 25:  # Increased sugar threshold for penalty
#         score -= 10  # High sugar penalty
#     if product_data.get('saturated_fat', 0) > 8:
#         score -= 10  # Reduced saturated fat penalty
#     if product_data.get('trans_fat', 0) > 0:
#         score -= 10  # Trans fat penalty

#     # Reward for natural ingredients and whole foods
#     if 'oats' in product_data.get('ingredients', '').lower() or 'nuts' in product_data.get('ingredients', '').lower():
#         score += 15  # Increase reward for whole grains and nuts

#     # Penalty for artificial additives
#     additives = ['preservatives', 'artificial', 'emulsifiers', 'stabilizers']
#     for additive in additives:
#         if additive in product_data.get('ingredients', '').lower():
#             score -= 3  # Reduced penalty for each artificial ingredient

#     # Reward for gluten-free products if the user has gluten restrictions
#     if 'gluten-free' in dietary_restrictions and 'wheat' not in product_data.get('allergens', '').lower():
#         score += 10

#     # Ensure score is within the 0-100 range
#     score = max(0, min(score, max_score))
    
#     # Scale score to 1-5
#     final_score = int(round((score / max_score) * 5))
#     final_score = max(1, min(final_score, 5))  # Ensure the final score is between 1 and 5
    
#     return final_score





def check_db_validity():
    """Check the validity of both user auth and product databases."""
    def check_user_auth_db():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA table_info(Users);")
            columns = cursor.fetchall()
            expected_columns = {'username', 'password', 'email', 'phone_number', 'registration_date'}
            actual_columns = {column[1] for column in columns}
            if not expected_columns.issubset(actual_columns):
                print("User auth DB is missing some expected columns.")
                return False
        except sqlite3.Error as e:
            print("User auth DB validation failed:", e)
            return False
        finally:
            conn.close()
        return True

    def check_product_db():
        conn = sqlite3.connect(PRODUCT_DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA table_info(Products);")
            columns = cursor.fetchall()
            expected_columns = {'barcode_num', 'product_name', 'ingredients', 'energy', 'proteins', 'carbohydrates', 'cholesterol', 'sugars', 'total_fat', 'saturated_fat',
                                       'trans_fat', 'sodium', 'fruits_vegetables_nuts', 'dietary_fibre', 'allergens', 'nutrition_grade', 'calcium', 'iodine', 'zinc', 'phosphorous', 'magnesium', 'vitamin_A', 'vitamin_B', 'vitamin_C', 'vitamin_D', 'vitamin_E', 'vitamin_K', 'other'
                                       }
        
            
            actual_columns = {column[1] for column in columns}
            if not expected_columns.issubset(actual_columns):
                print("Product DB is missing some expected columns.")
                return False
        except sqlite3.Error as e:
            print("Product DB validation failed:", e)
            return False
        finally:
            conn.close()
        return True

    user_db_valid = check_user_auth_db()
    product_db_valid = check_product_db()

    if not user_db_valid or not product_db_valid:
        print("One or both databases are not valid. Please check the database setup.")
        return False
    return True

def initialize_product_db():
    """Initialize the product database and ensure the Products table exists."""
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()
    
    # Drop table if it exists
    cursor.execute("DROP TABLE IF EXISTS Products")
    
    # Create the Products table with the specified schema
    cursor.execute("""
       CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode_num TEXT UNIQUE,
            product_name TEXT,
            ingredients TEXT,
            energy REAL,
            proteins REAL,
            carbohydrates REAL,
            cholesterol REAL,
            sugars REAL,
            total_fat REAL,
            saturated_fat REAL,
            trans_fat REAL,       
            sodium REAL,
            fruits_vegetables_nuts REAL,
            dietary_fibre REAL DEFAULT 0,
            allergens TEXT,
            nutrition_grade TEXT,
            calcium REAL DEFAULT 0,
            iodine REAL DEFAULT 0,
            zinc REAL DEFAULT 0,
            phosphorous REAL DEFAULT 0,
            magnesium REAL DEFAULT 0,
            vitamin_A REAL DEFAULT 0,
            vitamin_B REAL DEFAULT 0,
            vitamin_C REAL DEFAULT 0,
            vitamin_D REAL DEFAULT 0,
            vitamin_E REAL DEFAULT 0,
            vitamin_K REAL DEFAULT 0,
            other TEXT DEFAULT ""
        )
    """)
    
    conn.commit()
    conn.close()
    print("Product database initialized and schema created.")

def get_valid_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def get_valid_int(prompt, max_choice):
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= max_choice:
                return choice
            else:
                print(f"Invalid choice. Please enter a number between 1 and {max_choice}.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")




# def collect_form_data(username, form_data):
#     """Collect and store health data from the user."""
#     conn = sqlite3.connect(HEALTH_DB_PATH)
#     cursor = conn.cursor()

#     height = form_data.get('height')
#     weight = form_data.get('weight')
    
#     health_condition = form_data.getlist('health_condition')
#     allergies_option = form_data.get('allergies_option')
#     diet_type = form_data.get('diet_type')
#     health_goals = form_data.getlist('health_goals')
#     fitness_goals = form_data.getlist('fitness_goals')
#     weight_management_choice = form_data.get('weight_management_choice')
#     age = form_data.get('age')
    
#     try:
#         cursor.execute('''
#             INSERT INTO health_form (username, height, weight, health_condition, allergies_option, diet_type, health_goals, fitness_goals, age, weight_management_choice)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (username, height, weight, ','.join(health_condition), allergies_option, diet_type, ','.join(health_goals), ','.join(fitness_goals), age, weight_management_choice))
#         conn.commit()
#         print("Health data stored successfully!")
#     except sqlite3.Error as e:
#         print("Failed to store health data:", e)
#     finally:
#         conn.close()


# 

# def collect_form_data(username):
#     """Collect and store health data from the user."""
#     conn = sqlite3.connect(HEALTH_DB_PATH)
#     cursor = conn.cursor()

#     age = get_valid_int("Enter your age: ", 100)
#     height = get_valid_float("Enter your height (in cm): ")
#     weight = get_valid_float("Enter your weight (in kg): ")

#     print("What is your dietary type?")
#     print("1. Eggetarian 2. Vegetarian 3. Non-vegetarian 4. Jain")
#     diet_choice = get_valid_int("Your choice: ", 4)
#     diet_type = ['Eggetarian', 'Vegetarian', 'Non-vegetarian', 'Jain'][diet_choice - 1]

#     print("What chronic illnesses do you have? (separate multiple answers with commas)")
#     chronic_illness_choices = input("Your choices: ").split(',')
#     illness_map = ['Diabetes', 'Obesity', 'High blood pressure', 'Heart diseases', 'Lactose intolerance/food allergies', 'None']
#     chronic_illnesses = [illness_map[int(choice.strip()) - 1] for choice in chronic_illness_choices if choice.strip().isdigit()]

#     print("What specific dietary restrictions do you follow? (separate multiple answers with commas)")
#     dietary_restriction_choices = input("Your choices: ").split(',')
#     restriction_map = ['Low-sugar', 'Low-fat', 'Low-salt', 'Protein-rich', 'Anti-inflammatory', 'Gluten-free']
#     dietary_restrictions = [restriction_map[int(choice.strip()) - 1] for choice in dietary_restriction_choices if choice.strip().isdigit()]

#     print("Are there specific ingredients that trigger your condition(s) or cause discomfort? (separate multiple answers with commas)")
#     print("1. Sugar 2. Fats 3. Salt 4. Lactose 5. Wheat")
#     trigger_choices = input("Your choices: ").split(',')
#     trigger_map = ['Sugar', 'Fats', 'Salt', 'Lactose', 'Wheat']
#     trigger_ingredients = [trigger_map[int(choice.strip()) - 1] for choice in trigger_choices if choice.strip().isdigit()]

#     # Ensure trigger_ingredients is not empty
#     if not trigger_ingredients:
#         trigger_ingredients = ['None']

#     print("What health goal do you have? (separate multiple answers with commas)")
#     health_goal_choices = input("Your choices: ").split(',')
#     goal_map = ['Blood sugar control', 'Weight maintenance', 'Manage cholesterol', 'Blood pressure control', 'Bodybuilding', 'Control symptoms of your chronic illness', 'None']
#     health_goals = [goal_map[int(choice.strip()) - 1] for choice in health_goal_choices if choice.strip().isdigit()]

#     # Ensure health_goals is not empty
#     if not health_goals:
#         health_goals = ['None']

#     # Insert into database
#     cursor.execute('''
#     INSERT INTO health_form (username, age, height, weight, diet_type, chronic_illnesses, dietary_restrictions, trigger_ingredients, health_goals)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#     ''', (
#         username, age, height, weight, diet_type, 
#         ','.join(chronic_illnesses), 
#         ','.join(dietary_restrictions), 
#         ','.join(trigger_ingredients),  # Ensure list is properly joined
#         ','.join(health_goals)
#     ))

#     conn.commit()
#     conn.close()

#     return {
#         'What is your dietary type?': [diet_type],
#         'What chronic illnesses do you have? (separate multiple answers with commas)': chronic_illnesses,
#         'What specific dietary restrictions do you follow? (separate multiple answers with commas)': dietary_restrictions,
#         'Are there specific ingredients that trigger your condition(s) or cause discomfort? (separate multiple answers with commas)': trigger_ingredients,
#         'What health goal do you have? (separate multiple answers with commas)': health_goals
#     }





class Login:
    def __init__(self, username, password, conn=None):
        self.username = username
        self.password = password
        self.conn = sqlite3.connect(DB_PATH) if conn is None else conn

    def authenticate(self):
        try:
            hashed_password = hashlib.sha256(self.password.encode()).hexdigest()
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", 
                           (self.username, hashed_password))
            result = cursor.fetchone()
            if result:
                user_type = result[1] 
                print("Login successful!")
                return True, user_type
            else:
                print("Login failed. Invalid username or password.")
                return None, None
        except sqlite3.Error as e:
            print("Login failed:", e)
            return None, None
        finally:
            self.conn.close()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Login(username, password)
        status, user_type = user.authenticate()
        if status:
            if user_type == 'admin':
                session['username'] = username
                return redirect(url_for('admin_interface'))
            else:
                session['username'] = username
                return redirect(url_for('post_login_menu', username=username))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/admin_interface')
def admin_interface():
    if 'username' in session and session['username'] == 'admin':
        return render_template('admin_interface.html')
    else:
        return redirect(url_for('login'))




# class Register:
#     def __init__(self, form_data, conn=None):
#         self.conn = sqlite3.connect(DB_PATH) if conn is None else conn
#         self.data = {}
#         self.process_form_data(form_data)

#     def process_form_data(self, form_data):
#         # Process form data from the registration form
#         self.data['username'] = form_data.get('username')
#         self.data['password'] = form_data.get('password')
#         self.data['email'] = form_data.get('email')
#         self.data['phone_number'] = form_data.get('phone_number')

#     def collect_health_data(self, username):
#         """Collect health data for the user after registration."""
#         print(f"Collect health data for {username}")

#     def register_user(self):
#         try:
#             # Hash the password
#             hashed_password = hashlib.sha256(self.data['password'].encode()).hexdigest()
#             cursor = self.conn.cursor()

#             # Prepare other user data
#             username = self.data['username']
#             email = self.data['email']
#             phone_number = self.data.get('phone_number', '')
#             registration_date = datetime.datetime.now()

#             # Insert user data into the database
#             cursor.execute(""" 
#                 INSERT INTO Users (username, password, email, phone_number, registration_date)
#                 VALUES (?, ?, ?, ?, ?)
#             """, (username, hashed_password, email, phone_number, registration_date))
#             self.conn.commit()

#             # Collect health data after registration
#             self.collect_health_data(username)

#             print("Registration successful!")
#             return True
#         except sqlite3.Error as e:
#             print("Registration failed:", e)
#             return False
#         finally:
#             self.conn.close()

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         # Capture form data from the registration form
#         form_data = {
#             'username': request.form['username'],
#             'password': request.form['password'],
#             'email': request.form['email'],
#             'phone_number': request.form.get('phone_number', '')
#         }

#         # Create a Register object and attempt to register the user
#         user_registration = Register(form_data)
#         registration_result = user_registration.register_user()

#         if registration_result:
#             # Store username in the session after successful registration
#             session['username'] = form_data['username']
#             return redirect(url_for('health_form', username=form_data['username']))
#         else:
#             return "Registration failed. Please try again."

#     return render_template('register.html')

# @app.route('/health_form/<username>', methods=['GET', 'POST'])
# def health_form(username):
#     if 'username' in session and session['username'] == username:
#         if request.method == 'POST':
#             # Pass form data to collect_form_data function
#             collect_form_data(username, request.form)
#             return "Health data submitted successfully!"
#         return render_template('health_form.html', username=username)
#     else:
#         return redirect(url_for('login'))
    

def collect_form_data(username):
    """Collect and store health data from the user."""
    conn = sqlite3.connect(HEALTH_DB_PATH)
    cursor = conn.cursor()

    age = get_valid_int("Enter your age: ", 100)
    height = get_valid_float("Enter your height (in cm): ")
    weight = get_valid_float("Enter your weight (in kg): ")

    print("What is your dietary type?")
    print("1. Eggetarian 2. Vegetarian 3. Non-vegetarian 4. Jain")
    diet_choice = get_valid_int("Your choice: ", 4)
    diet_type = ['Eggetarian', 'Vegetarian', 'Non-vegetarian', 'Jain'][diet_choice-1]

    print("What chronic illnesses do you have? (separate multiple answers with commas)")
    print("1. Diabetes 2. Obesity 3. High blood pressure 4. Heart diseases 5. Lactose intolerance/food allergies 6. None")
    chronic_illness_choices = input("Your choices: ").split(',')
    illness_map = ['Diabetes', 'Obesity', 'High blood pressure', 'Heart diseases', 'Lactose intolerance/food allergies', 'None']
    try:
        chronic_illnesses = [illness_map[int(choice.strip())-1] for choice in chronic_illness_choices]
    except (IndexError, ValueError):
        print("Invalid choice(s). Defaulting to 'None'.")
        chronic_illnesses = ['None']

    print("What specific dietary restrictions do you follow? (separate multiple answers with commas)")
    print("1. Low-sugar 2. Low-fat 3. Low-salt 4. Protein-rich 5. Anti-inflammatory 6. Gluten-free")
    dietary_restriction_choices = input("Your choices: ").split(',')
    restriction_map = ['Low-sugar', 'Low-fat', 'Low-salt', 'Protein-rich', 'Anti-inflammatory', 'Gluten-free']
    try:
        dietary_restrictions = [restriction_map[int(choice.strip())-1] for choice in dietary_restriction_choices]
    except (IndexError, ValueError):
        print("Invalid choice(s). No dietary restrictions recorded.")
        dietary_restrictions = []

    print("Are there specific ingredients that trigger your condition(s) or cause discomfort? (separate multiple answers with commas)")
    print("1. Sugar 2. Fats 3. Salt 4. Lactose 5. Wheat")
    trigger_choices = input("Your choices: ").split(',')
    trigger_map = ['Sugar', 'Fats', 'Salt', 'Lactose', 'Wheat']
    try:
        trigger_ingredients = [trigger_map[int(choice.strip())-1] for choice in trigger_choices]
    except (IndexError, ValueError):
        print("Invalid choice(s). No trigger ingredients recorded.")
        trigger_ingredients = []


    print("What health goal do you have? (separate multiple answers with commas)")
    print("1. Blood sugar control 2. Weight maintenance 3. Manage cholesterol 4. Blood pressure control 5. Bodybuilding 6. Control symptoms of your chronic illness 7. None")
    health_goal_choices = input("Your choices: ").split(',')
    goal_map = ['Blood sugar control', 'Weight maintenance', 'Manage cholesterol', 'Blood pressure control', 'Bodybuilding', 'Control symptoms of your chronic illness', 'None']
    try:
        health_goals = [goal_map[int(choice.strip())-1] for choice in health_goal_choices]
    except (IndexError, ValueError):
        print("Invalid choice(s). Defaulting to 'None'.")
        health_goals = ['None']

    cursor.execute('''
    INSERT INTO health_form (username, age, height, weight, diet_type, chronic_illnesses, dietary_restrictions, trigger_ingredients, health_goals)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, age, height, weight, diet_type,','.join(chronic_illnesses),','.join(dietary_restrictions), ','.join(trigger_ingredients), ','.join(health_goals)))

    conn.commit()
    conn.close()

    return {
        'What is your dietary type?': [diet_type],
        'What chronic illnesses do you have? (separate multiple answers with commas)': chronic_illnesses,
        'What specific dietary restrictions do you follow? (separate multiple answers with commas)': dietary_restrictions,
        'Are there specific ingredients that trigger your condition(s) or cause discomfort? (separate multiple answers with commas)': trigger_ingredients,
        'What health goal do you have? (separate multiple answers with commas)': health_goals
    }

class Register:
    def __init__(self, form_data, conn=None):
        self.conn = sqlite3.connect(DB_PATH) if conn is None else conn
        self.data = {}
        self.process_form_data(form_data)

    def process_form_data(self, form_data):
        # Process form data from the registration form
        self.data['username'] = form_data.get('username')
        self.data['password'] = form_data.get('password')
        self.data['email'] = form_data.get('email')
        self.data['phone_number'] = form_data.get('phone_number')

    def collect_health_data(self, username, form_data):
        """Collect and store health data for the user after registration."""
        conn = sqlite3.connect(HEALTH_DB_PATH)
        cursor = conn.cursor()

        age = form_data.get('age')
        height = form_data.get('height')
        weight = form_data.get('weight')
        diet_type = form_data.get('diet_type')

        chronic_illnesses = form_data.get('chronic_illnesses').split(',')
        dietary_restrictions = form_data.get('dietary_restrictions').split(',')
        trigger_ingredients = form_data.get('trigger_ingredients').split(',')
        health_goals = form_data.get('health_goals').split(',')

        cursor.execute('''
        INSERT INTO health_form (username, age, height, weight, diet_type, chronic_illnesses, dietary_restrictions, trigger_ingredients, health_goals)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, age, height, weight, diet_type, ','.join(chronic_illnesses), ','.join(dietary_restrictions), ','.join(trigger_ingredients), ','.join(health_goals)))

        conn.commit()
        conn.close()

    def register_user(self):
        try:
            # Hash the password
            hashed_password = hashlib.sha256(self.data['password'].encode()).hexdigest()
            cursor = self.conn.cursor()

            # Prepare other user data
            username = self.data['username']
            email = self.data['email']
            phone_number = self.data.get('phone_number', '')
            registration_date = datetime.datetime.now()

            # Insert user data into the database
            cursor.execute(""" 
                INSERT INTO Users (username, password, email, phone_number, registration_date)
                VALUES (?, ?, ?, ?, ?)
            """, (username, hashed_password, email, phone_number, registration_date))
            self.conn.commit()

            print("Registration successful!")
            return True
        except sqlite3.Error as e:
            print("Registration failed:", e)
            return False
        finally:
            self.conn.close()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Capture form data from the registration form
        form_data = {
            'username': request.form['username'],
            'password': request.form['password'],
            'email': request.form['email'],
            'phone_number': request.form.get('phone_number', '')
        }

        # Create a Register object and attempt to register the user
        user_registration = Register(form_data)
        registration_result = user_registration.register_user()

        if registration_result:
            # Store username in the session after successful registration
            session['username'] = form_data['username']
            return redirect(url_for('health_form', username=form_data['username']))
        else:
            return "Registration failed. Please try again."

    return render_template('register.html')


@app.route('/health_form/<username>', methods=['GET', 'POST'])
def health_form(username):
    if 'username' in session and session['username'] == username:
        if request.method == 'POST':
            # Pass form data to collect_health_data method of the Register class
            form_data = request.form.to_dict()
            user_registration = Register({})
            user_registration.collect_health_data(username, form_data)
            flash("Health data submitted successfully!", "success")
            
            return redirect(url_for('login'))
        return render_template('health_form.html', username=username)
    else:
        return redirect(url_for('login'))







# Utility functions for input validation
def get_valid_int(prompt, max_value):
    while True:
        try:
            value = int(input(prompt))
            if 0 <= value <= max_value:
                return value
            else:
                print(f"Please enter a valid number between 0 and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def get_valid_float(prompt):
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def admin_interface():
    """Admin functionalities for managing users and products."""
    while True:
        print("\n--- Admin Interface ---")
        print("1: View Auth DB")
        print("2: Add User")
        print("3: Remove User")
        print("4: Change User Password")
        print("5: Add Products and Nutrient Info")
        print("6: Delete Product from Database")
        print("7: View All Products")
        print("8: Back to Main Menu")

        try:
            choice = int(input("Select an option: "))
            if choice == 1:
                view_auth_db()
            elif choice == 2:
                add_user()
            elif choice == 3:
                remove_user()
            elif choice == 4:
                change_user_password()
            elif choice == 5:
                add_product()
            elif choice == 6:
                delete_product()
            elif choice == 7:
                view_all_products()
            elif choice == 8:
                break  # Back to main menu
            else:
                print("Invalid option. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def calculate_nutri_score(data, moist):
    nutri_score = NutriScore()
    result = nutri_score.calculate_class(data, moist)
    print(f"The Nutri-Score for this product is: {result}")
    return result

def post_login_menu(username):
    while True:
        print("\n--- Post-Login Menu ---")
        print("1: View product information via Scanning Barcode")
        print("2: View product information via barcode number")
        print("3: User Profile Interface")
        print("4: Log Out")
        print("5: View shopping list")
        print("6: View favourite list")
        print("7: Delete from shopping list")
        print("8: Delete from favourite list")
        
        try:
            choice = int(input("Select an option: "))
            if choice == 1:
                use_custom_url = input("Do you want to use a custom IP address? (y/n): ").lower() == 'y'
                scan_barcode(username) 
            elif choice == 2:
                barcode = input("Enter the barcode number: ")
                display_product_info(username,barcode)
            elif choice == 3:
                view_profile(username)  # Ensure the username is passed
            elif choice == 4:
                log_out()
                break
            elif choice == 5:
                view_shopping_list(username)
            elif choice == 6:
                view_fav_list(username)   
            elif choice == 7 : 
                product_name_shop = input("Enter the name of the product to delete: ").strip()
                quantity_to_delete_shop = int(input("Enter the quantity to delete: "))
                delete_from_shopping_list(username, product_name_shop, quantity_to_delete_shop)  
            elif choice == 8:
                product_name_fav = input("Enter the name of the product to delete: ").strip()
                quantity_to_delete_fav = int(input("Enter the quantity to delete: "))
                delete_from_fav_list(username, product_name_fav, quantity_to_delete_fav)
        except ValueError:
            print("Invalid input. Please enter a number.")
            






# @app.route('/post_login_menu', methods=['GET', 'POST'])
# def post_login_menu():
#     if 'username' not in session:
#         return redirect(url_for('login'))
    
#     username = session['username']

#     if request.method == 'POST':
#         barcode_num = request.form.get('barcode_num')

       
#         # Fetch product info using the input barcode number
#         product_info = get_product_info(barcode_num)

#         if product_info:
#             # Render the product details page with the product info
#             return render_template('product_info.html', product=product_info)
#         else:

#             return render_template('post_login_menu.html', username=username)

#     return render_template('post_login_menu.html', username=username)



def search_product_by_name(product_name):
    """Search for products by name (case insensitive) and return matching options."""
    # Connect to the SQLite database
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()
    results = []

    try:
        # Query to fetch all products where the name matches the input, case-insensitive
        query = """
        SELECT id, barcode_num, product_name, ingredients, energy, proteins, carbohydrates, cholesterol, sugars, total_fat, saturated_fat,
               trans_fat, sodium, fruits_vegetables_nuts, dietary_fibre, allergens, nutrition_grade
        FROM products
        WHERE LOWER(product_name) LIKE ?
        """
        # Execute the query with the product name, using wildcard matching
        cursor.execute(query, ('%' + product_name.lower() + '%',))
        # Fetch all matching results
        results = cursor.fetchall()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the database connection
        conn.close()

    return results



@app.route('/search_product_by_name', methods=['POST'])
def search_product_by_name():
    """Search for products by name and return product info."""
    product_name = request.form.get('product_name').strip().lower()
    
    # Connect to the SQLite database
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT id, barcode_num, product_name, ingredients, energy, proteins, carbohydrates, cholesterol, sugars, total_fat, saturated_fat,
               trans_fat, sodium, fruits_vegetables_nuts, dietary_fibre, allergens, nutrition_grade
        FROM products
        WHERE LOWER(product_name) LIKE ?
        """
        cursor.execute(query, ('%' + product_name + '%',))
        results = cursor.fetchall()
        
        if results:
            # Assume we only care about the first match for simplicity
            product = results[0]
            product_info = {
                'id': product[0],
                'barcode_num': product[1],
                'product_name': product[2],
                'ingredients': product[3],
                'energy': product[4],
                'proteins': product[5],
                'carbohydrates': product[6],
                'cholesterol': product[7],
                'sugars': product[8],
                'total_fat': product[9],
                'saturated_fat': product[10],
                'trans_fat': product[11],
                'sodium': product[12],
                'fruits_vegetables_nuts': product[13],
                'dietary_fibre': product[14],
                'allergens': product[15],
                'nutrition_grade': product[16],
            }
            return render_template('product_name.html', product=product_info)
        else:
            return redirect(url_for('post_login_menu', error="No products found."))
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return redirect(url_for('post_login_menu', error="An error occurred while searching."))
    finally:
        conn.close()


# @app.route('/post_login_menu', methods=['GET', 'POST'])
# def post_login_menu():
#     if 'username' not in session:
#         return redirect(url_for('login'))

#     username = session['username']

#     if request.method == 'POST':
#         barcode_num = request.form.get('barcode_num')
#         product_name = request.form.get('product_name')

#         # Check if barcode number is provided
#         if barcode_num:
#             # Fetch product info using the input barcode number
#             product_info = get_product_info(barcode_num)
#             if product_info:
#                 return render_template('product_info.html', product=product_info)
#             else:
#                 return render_template('post_login_menu.html', username=username, error="No product found with the given barcode.")

#         # Check if product name is provided
#         if product_name:
#             # Search for products by name
#             matching_products = search_product_by_name(product_name)
#             if matching_products:
#                 # Redirect to product_info.html with the first matching product
#                 first_product = matching_products[0]
#                 product_info = {
#                     'id': first_product[0],
#                     'barcode_num': first_product[1],
#                     'product_name': first_product[2],
#                     'ingredients': first_product[3],
#                     'energy': first_product[4],
#                     'proteins': first_product[5],
#                     'carbohydrates': first_product[6],
#                     'cholesterol': first_product[7],
#                     'sugars': first_product[8],
#                     'total_fat': first_product[9],
#                     'saturated_fat': first_product[10],
#                     'trans_fat': first_product[11],
#                     'sodium': first_product[12],
#                     'fruits_vegetables_nuts': first_product[13],
#                     'dietary_fibre': first_product[14],
#                     'allergens': first_product[15],
#                     'nutrition_grade': first_product[16],
#                 }
#                 return render_template('product_name.html', product=product_info)
#             else:
#                 return render_template('post_login_menu.html', username=username, error="No products found matching the entered name.")

#     return render_template('post_login_menu.html', username=username)

# API endpoints for product lookup



def insert_product_data(product_data):
    """Insert product data into the Products table."""
    connection = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = connection.cursor()

    # Define the insert query
    query = """
    INSERT INTO Products (
        barcode_num, product_name, ingredients, energy, proteins, carbohydrates,
        cholesterol, sugars, total_fat, saturated_fat, trans_fat, sodium,
        fruits_vegetables_nuts, dietary_fibre, allergens, nutrition_grade
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # Extract values from product_data dictionary
    values = (
        product_data.get("barcode_num"),
        product_data.get("product_name"),
        product_data.get("ingredients"),
        product_data.get("energy"),
        product_data.get("proteins"),
        product_data.get("carbohydrates"),
        product_data.get("cholesterol"),
        product_data.get("sugars"),
        product_data.get("total_fat"),
        product_data.get("saturated_fat"),
        product_data.get("trans_fat"),
        product_data.get("sodium"),
        product_data.get("fruits_vegetables_nuts"),
        product_data.get("dietary_fibre"),
        product_data.get("allergens"),
        product_data.get("nutrition_grade"),
    )

    # Execute the insert query
    cursor.execute(query, values)
    connection.commit()
    connection.close()


# import requests

# API_ENDPOINTS = [
#     "https://world.openfoodfacts.org/api/v0/product/{barcode}.json",
#     "https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}"
# ]
 

# @app.route('/post_login_menu', methods=['GET', 'POST'])
# def post_login_menu():
#     if 'username' not in session:
#         return redirect(url_for('login'))

#     username = session['username']

#     if request.method == 'POST':
#         barcode_num = request.form.get('barcode_num')
#         product_name = request.form.get('product_name')

#         # Check if barcode number is provided
#         if barcode_num:
#             # Fetch product info using the input barcode number
#             product_info = get_product_info(barcode_num)
#             if product_info:
#                 return render_template('product_info.html', product=product_info)
#             else:
#                 # If not found in the database, fetch from external API
#                 product_data = {"barcode_num": barcode_num}  # Initialize with barcode
#                 api_success = False

#                 for endpoint in API_ENDPOINTS:
#                     try:
#                         response = requests.get(endpoint.format(barcode=barcode_num))
#                         if response.status_code == 200:
#                             data = response.json()

#                             # Parse API response to get product details
#                             if "product" in data and data["product"]:
#                                 product_data.update({
#                                     'product_name': data["product"].get('product_name', 'Unknown'),
#                                     'ingredients': data["product"].get('ingredients_text', 'Unknown'),
#                                     'energy': data["product"].get('nutriments', {}).get('energy-kcal_100g', 0),
#                                     'proteins': data["product"].get('nutriments', {}).get('proteins_100g', 0),
#                                     'carbohydrates': data["product"].get('nutriments', {}).get('carbohydrates_100g', 0),
#                                     'cholesterol': data["product"].get('nutriments', {}).get('cholesterol_100g', 0),
#                                     'sugars': data["product"].get('nutriments', {}).get('sugars_100g', 0),
#                                     'total_fat': data["product"].get('nutriments', {}).get('fat_100g', 0),
#                                     'saturated_fat': data["product"].get('nutriments', {}).get('saturated-fat_100g', 0),
#                                     'trans_fat': data["product"].get('nutriments', {}).get('trans-fat_100g', 0),
#                                     'sodium': data["product"].get('nutriments', {}).get('sodium_100g', 0),
#                                     'allergens': data["product"].get('allergens', 'Unknown'),
#                                     'nutrition_grade': data["product"].get('nutrition_grades_tags', ['Unknown'])[0]
#                                 })
#                                 api_success = True
#                                 break  # Stop searching once we have the data
#                     except Exception as e:
#                         print(f"API error: {e}")  # Log any API error

#                 if api_success:
#                     # Insert fetched product data into the database
#                     insert_product_data(product_data)
#                     return render_template('product_info.html', product=product_data)
#                 else:
#                     return render_template(
#                         'post_login_menu.html', 
#                         username=username, 
#                         error="No product found with the given barcode, even from external sources."
#                     )

#         # Check if product name is provided
#         if product_name:
#             # Search for products by name
#             matching_products = search_product_by_name(product_name)
#             if matching_products:
#                 # Redirect to product_info.html with the first matching product
#                 first_product = matching_products[0]
#                 product_info = {
#                     'id': first_product[0],
#                     'barcode_num': first_product[1],
#                     'product_name': first_product[2],
#                     'ingredients': first_product[3],
#                     'energy': first_product[4],
#                     'proteins': first_product[5],
#                     'carbohydrates': first_product[6],
#                     'cholesterol': first_product[7],
#                     'sugars': first_product[8],
#                     'total_fat': first_product[9],
#                     'saturated_fat': first_product[10],
#                     'trans_fat': first_product[11],
#                     'sodium': first_product[12],
#                     'fruits_vegetables_nuts': first_product[13],
#                     'dietary_fibre': first_product[14],
#                     'allergens': first_product[15],
#                     'nutrition_grade': first_product[16],
#                 }
#                 return render_template('product_name.html', product=product_info)
#             else:
#                 return render_template(
#                     'post_login_menu.html', 
#                     username=username, 
#                     error="No products found matching the entered name."
#                 )

#     return render_template('post_login_menu.html', username=username)


import sqlite3
import requests
from PIL import Image
from io import BytesIO
import os

# Database path
PRODUCT_DB_PATH = 'product_information.db'

# Directory for saving product images
IMAGE_SAVE_PATH = os.path.join('static', 'product_images')

# API endpoints for product lookup (add more endpoints as needed)
API_ENDPOINTS = [
    "https://world.openfoodfacts.org/api/v0/product/{barcode}.json",
    "https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}"
]

# Ensure image save path exists
os.makedirs(IMAGE_SAVE_PATH, exist_ok=True)

# Fetch product data from APIs
def fetch_product_data(barcode):
    product_data = {"barcode_num": barcode}  # Initialize with the barcode
    product_image_url = None

    for endpoint in API_ENDPOINTS:
        url = endpoint.format(barcode=barcode)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'product' in data:
                    product = data['product']
                    # Format allergens field
                    allergens = product.get("allergens", "N/A")
                    formatted_allergens = (
                        ", ".join([a.split(":")[-1].capitalize() for a in allergens.split(",")])
                        if allergens != "N/A" else "N/A"
                    )
                    product_data.update({
                        "product_name": product.get("product_name", "N/A"),
                        "ingredients": product.get("ingredients_text", "N/A"),
                        "energy": product.get("nutriments", {}).get("energy_100g", 0),
                        "proteins": product.get("nutriments", {}).get("proteins_100g", 0),
                        "carbohydrates": product.get("nutriments", {}).get("carbohydrates_100g", 0),
                        "cholesterol": product.get("nutriments", {}).get("cholesterol_100g", 0),
                        "sugars": product.get("nutriments", {}).get("sugars_100g", 0),
                        "total_fat": product.get("nutriments", {}).get("fat_100g", 0),
                        "saturated_fat": product.get("nutriments", {}).get("saturated-fat_100g", 0),
                        "trans_fat": product.get("nutriments", {}).get("trans-fat_100g", 0),
                        "sodium": product.get("nutriments", {}).get("sodium_100g", 0),
                        "fruits_vegetables_nuts": product.get("nutriments", {}).get("fruits-vegetables-nuts_100g", 0),
                        "dietary_fibre": product.get("nutriments", {}).get("fiber_100g", 0),
                        "allergens": formatted_allergens,
                        "nutrition_grade": product.get("nutrition_grades", "N/A").upper() if product.get("nutrition_grades") else "N/A",
                    })
                    # Get the product image URL
                    product_image_url = product.get("image_url")
                elif 'items' in data and data['items']:
                    item = data['items'][0]
                    product_data.update({
                        "product_name": item.get("title", "N/A"),
                        # Add other fields if needed...
                    })
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
    return product_data, product_image_url

# Download and resize product image
def download_and_resize_image(image_url, save_path):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            # Resize image to height = 250 pixels, maintaining aspect ratio
            width, height = image.size
            new_height = 250
            new_width = int((new_height / height) * width)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            # Save the image
            image.save(save_path)
            print(f"Image saved at: {save_path}")
    except Exception as e:
        print(f"Error downloading or resizing image: {e}")


# Insert product into the database
def save_product_to_db(data):
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Products (
                barcode_num, product_name, ingredients, energy, proteins, carbohydrates, cholesterol, 
                sugars, total_fat, saturated_fat, trans_fat, sodium, fruits_vegetables_nuts, dietary_fibre, 
                allergens, nutrition_grade
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['barcode_num'], data['product_name'], data['ingredients'], data['energy'], data['proteins'], 
            data['carbohydrates'], data['cholesterol'], data['sugars'], data['total_fat'], data['saturated_fat'], 
            data['trans_fat'], data['sodium'], data['fruits_vegetables_nuts'], data['dietary_fibre'], 
            data['allergens'], data['nutrition_grade']
        ))
        conn.commit()
        print("Product saved successfully.")
    except sqlite3.IntegrityError:
        print("Product with this barcode already exists.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

# Main function
def main():
    barcode = input("Enter a 13-digit barcode number: ").strip()
    if len(barcode) != 13 or not barcode.isdigit():
        print("Invalid barcode number. Please enter a valid 13-digit barcode.")
        return

    # Check if the product already exists in the database
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE barcode_num = ?", (barcode,))
    existing_product = cursor.fetchone()
    conn.close()

    if existing_product:
        print("Product with this barcode already exists in the database.")
    else:
        # Fetch product data from APIs
        fetched_data, image_url = fetch_product_data(barcode)
        if not fetched_data:
            print(f"No data found for barcode {barcode}.")
            return

        # Display fetched data for user confirmation
        print("\nFetched product data:")
        for key, value in fetched_data.items():
            print(f"{key}: {value}")

        confirm = input("\nDo you want to add this product to the database? (Y/N): ").strip().upper()
        if confirm == 'Y':
            # Save product data to database
            save_product_to_db(fetched_data)

            # Download and save product image
            if image_url:
                image_path = os.path.join(IMAGE_SAVE_PATH, f"{barcode}.jpg")
                download_and_resize_image(image_url, image_path)
            else:
                print("No image URL found for this product.")





@app.route('/post_login_menu', methods=['GET', 'POST'])
def post_login_menu():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    if request.method == 'POST':
        barcode_num = request.form.get('barcode_num')
        product_name = request.form.get('product_name')

        # Check if barcode number is provided
        if barcode_num:
            # Fetch product info using the input barcode number
            product_info = get_product_info(barcode_num)
            if product_info:
                return render_template('product_info.html', product=product_info)
            else:
                # If not found in the database, fetch from external API
                product_data = {"barcode_num": barcode_num}  # Initialize with barcode
                product_image_url = None
                api_success = False

                for endpoint in API_ENDPOINTS:
                    try:
                        response = requests.get(endpoint.format(barcode=barcode_num))
                        if response.status_code == 200:
                            data = response.json()

                            # Parse API response to get product details
                            if "product" in data and data["product"]:
                                product = data["product"]
                                product_data.update({
                                    'product_name': product.get('product_name', 'Unknown'),
                                    'ingredients': product.get('ingredients_text', 'Unknown'),
                                    'energy': product.get('nutriments', {}).get('energy-kcal_100g', 0),
                                    'proteins': product.get('nutriments', {}).get('proteins_100g', 0),
                                    'carbohydrates': product.get('nutriments', {}).get('carbohydrates_100g', 0),
                                    'cholesterol': product.get('nutriments', {}).get('cholesterol_100g', 0),
                                    'sugars': product.get('nutriments', {}).get('sugars_100g', 0),
                                    'total_fat': product.get('nutriments', {}).get('fat_100g', 0),
                                    'saturated_fat': product.get('nutriments', {}).get('saturated-fat_100g', 0),
                                    'trans_fat': product.get('nutriments', {}).get('trans-fat_100g', 0),
                                    'sodium': product.get('nutriments', {}).get('sodium_100g', 0),
                                    'fruits_vegetables_nuts': product.get('nutriments', {}).get('fruits-vegetables-nuts_100g', 0),
                                    'dietary_fibre': product.get('nutriments', {}).get('fiber_100g', 0),
                                    'allergens': product.get('allergens', 'Unknown'),
                                    'nutrition_grade': product.get('nutrition_grades_tags', ['Unknown'])[0]
                                })
                                product_image_url = product.get('image_url')
                                api_success = True
                                break  # Stop searching once we have the data
                    except Exception as e:
                        print(f"API error: {e}")  # Log any API error

                if api_success:
                    # Insert fetched product data into the database
                    insert_product_data(product_data)

                    # Save product image if available
                    if product_image_url:
                        image_save_path = os.path.join(IMAGE_SAVE_PATH, f"{barcode_num}.jpg")
                        download_and_resize_image(product_image_url, image_save_path)
                        product_data['image_path'] = image_save_path

                    return render_template('product_info.html', product=product_data)
                else:
                    return render_template(
                        'post_login_menu.html',
                        username=username,
                        error="No product found with the given barcode, even from external sources."
                    )

        # Check if product name is provided
        if product_name:
            # Search for products by name
            matching_products = search_product_by_name(product_name)
            if matching_products:
                # Redirect to product_info.html with the first matching product
                first_product = matching_products[0]
                product_info = {
                    'id': first_product[0],
                    'barcode_num': first_product[1],
                    'product_name': first_product[2],
                    'ingredients': first_product[3],
                    'energy': first_product[4],
                    'proteins': first_product[5],
                    'carbohydrates': first_product[6],
                    'cholesterol': first_product[7],
                    'sugars': first_product[8],
                    'total_fat': first_product[9],
                    'saturated_fat': first_product[10],
                    'trans_fat': first_product[11],
                    'sodium': first_product[12],
                    'fruits_vegetables_nuts': first_product[13],
                    'dietary_fibre': first_product[14],
                    'allergens': first_product[15],
                    'nutrition_grade': first_product[16],
                }
                return render_template('product_info.html', product=product_info)
            else:
                return render_template(
                    'post_login_menu.html',
                    username=username,
                    error="No products found matching the entered name."
                )

    return render_template('post_login_menu.html', username=username)



def view_profile(username):
    """Display the profile menu and handle user input."""
    while True:
        print(f"\n--- View Profile for {username} ---")
        print("1: Change Password")
        print("2: Log Out")
        print("3: Change Account Info")
        print("4: View User Profile Questions & Answers")
        print("5: Edit Your Answers")
        print("6: Favourite Items")
        print("7: Edit Goals")
        print("8: Wishlist")
        print("9: My Past Orders")
        print("10: Cart")
        print("11: Change Payment Information")
        print("12: Health Chart")
        print("13: Savings Chart")

        try:
            choice = int(input("Select an option: "))
            if choice == 1:
                change_password(username)
            elif choice == 2:
                if log_out():
                    break
            elif choice == 3:
                change_account_info(username)
            elif choice == 4:
                view_user_questions(username)
            elif choice == 5:
                edit_user_questions(username)
            elif choice == 6:
                view_fav_list(username)
            elif 7 <= choice <= 9:
                print(f"Feature {choice}: Placeholder for the selected option.")
            elif choice == 10:
                view_shopping_list(username)
            elif 11 <= choice <= 13:
                print(f"Feature {choice}: Placeholder for the selected option.")
            else:
                print("Invalid option. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number.")

@app.route('/view_profile')
def view_profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    return render_template('view_profile.html', username=username)




def view_user_questions(username):
    """Display the user's profile questions and answers."""
    conn = sqlite3.connect(HEALTH_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_form WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    conn.close()

@app.route('/view_user_questions')
def view_user_questions():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = sqlite3.connect(HEALTH_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_form WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return render_template('view_user_questions.html', data=result)
    else:
        flash("User profile data not found.", "error")
        return redirect(url_for('view_profile'))




# def edit_user_questions(username):
#     """Allow the user to edit their profile questions."""
#     conn = sqlite3.connect(HEALTH_DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM health_form WHERE username = ?", (username,))
#     result = cursor.fetchone()
#     if result:
#         print("\n--- Edit Your Profile Questions ---")
#         height = input(f"Height (current: {result[2]} cm): ")
#         weight = input(f"Weight (current: {result[3]} kg): ")
        
#         print("Select your health conditions (comma-separated numbers):")
#         print("1. Obesity 2. Lactose Intolerance 3. Allergies 4. PCOS 5. Diabetes 6. Hypertension 7. NA")
#         health_conditions = input(f"Health Conditions (current: {result[4]}): ")
        
#         # Handle Allergies
#         allergies_option = result[5]
#         if 'Allergies' in health_conditions:
#             print("Select your allergies (comma-separated numbers):")
#             print("1. Dairy 2. Nuts 3. Gluten")
#             allergies_choices = input(f"Allergies (current: {result[5]}): ").split(',')
#             allergies_map = ['Dairy', 'Nuts', 'Gluten']
#             try:
#                 allergies_option = [allergies_map[int(choice)-1] for choice in allergies_choices]
#                 allergies_option = ','.join(allergies_option)
#             except (IndexError, ValueError):
#                 print("Invalid choice(s). No allergies recorded.")
#                 allergies_option = None

#         print("Select your diet type:")
#         print("1. Eggetarian 2. Vegetarian 3. Non-vegetarian 4. Jain")
#         diet_type = input(f"Diet Type (current: {result[6]}): ")
        
#         print("Select your health goals (comma-separated numbers):")
#         print("1. BP/Sugar Control 2. Manage Cholesterol 3. NA")
#         health_goals = input(f"Health Goals (current: {result[7]}): ")
        
#         print("Select your fitness goals (comma-separated numbers):")
#         print("1. Weight Management 2. Lifestyle Management 3. Muscle Gain 4. Controlled Diet 5. NA")
#         fitness_goals = input(f"Fitness Goals (current: {result[8]}): ")
        
#         age = input(f"Age (current: {result[9]}): ")
        
#         weight_management_choice = None
#         if 'Weight Management' in fitness_goals:
#             print("For Weight Management, select your specific goal:")
#             print("1. Ideal Weight 2. Gain 3. Loss")
#             wm_choice = get_valid_int("Your choice: ", 3)
#             weight_management_choice_map = ['Ideal Weight', 'Gain', 'Loss']
#             weight_management_choice = weight_management_choice_map[wm_choice-1]

#         # Update the database with new values (if any were provided)
#         cursor.execute('''UPDATE health_form 
#                           SET height = ?, weight = ?, health_condition = ?, allergies_option = ?, 
#                               diet_type = ?, health_goals = ?, fitness_goals = ?, age = ?, 
#                               weight_management_choice = ?
#                           WHERE username = ?''',
#                        (height or result[1], 
#                         weight or result[2], 
#                         health_conditions or result[4], 
#                         allergies_option or result[5], 
#                         diet_type or result[6], 
#                         health_goals or result[7], 
#                         fitness_goals or result[8], 
#                         age or result[9], 
#                         weight_management_choice or result[10], 
#                         username))

#         conn.commit()
#         print("Profile updated successfully.")
#     else:
#         print("User profile data not found.")
#     conn.close()

# @app.route('/edit_user_questions', methods=['GET', 'POST'])
# def edit_user_questions():
#     if 'username' not in session:
#         return redirect(url_for('login'))

#     username = session['username']
#     conn = sqlite3.connect(HEALTH_DB_PATH)
#     cursor = conn.cursor()

#     if request.method == 'POST':
#         height = request.form.get('height')
#         weight = request.form.get('weight')
#         health_conditions = request.form.get('health_conditions')
#         allergies_option = request.form.get('allergies_option')
#         diet_type = request.form.get('diet_type')
#         health_goals = request.form.get('health_goals')
#         fitness_goals = request.form.get('fitness_goals')
#         age = request.form.get('age')
#         weight_management_choice = request.form.get('weight_management_choice')

#         cursor.execute('''UPDATE health_form 
#                           SET height = ?, weight = ?, health_condition = ?, allergies_option = ?, 
#                               diet_type = ?, health_goals = ?, fitness_goals = ?, age = ?, 
#                               weight_management_choice = ?
#                           WHERE username = ?''',
#                        (height or None, 
#                         weight or None, 
#                         health_conditions or None, 
#                         allergies_option or None, 
#                         diet_type or None, 
#                         health_goals or None, 
#                         fitness_goals or None, 
#                         age or None, 
#                         weight_management_choice or None, 
#                         username))

#         conn.commit()
#         conn.close()
#         flash("Profile updated successfully.", "success")
#         return redirect(url_for('view_user_questions'))

#     # For GET request, fetch current user data to populate the form
#     cursor.execute("SELECT * FROM health_form WHERE username = ?", (username,))
#     result = cursor.fetchone()
#     conn.close()

#     if result:
#         return render_template('edit_user_questions.html', data=result)
#     else:
#         flash("User profile data not found.", "error")
#         return redirect(url_for('view_profile'))

def edit_user_questions(username):
    """Allow the user to edit their profile questions."""
    conn = sqlite3.connect(HEALTH_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM health_form WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if result:
        # Prompt for new height and weight
        height = get_valid_float("Enter your height (in cm): ")
        weight = get_valid_float("Enter your weight (in kg): ")

        # Update other fields based on current values
        age = input(f"Age (current: {result[2]}): ")
        
        print("What is your dietary type? Current: ", result[4])
        print("1. Eggetarian 2. Vegetarian 3. Non-vegetarian 4. Jain")
        diet_choice = input("Enter new choice or press Enter to keep current: ")
        if diet_choice:
            diet_type = ['Eggetarian', 'Vegetarian', 'Non-vegetarian', 'Jain'][int(diet_choice) - 1] if diet_choice in ['1', '2', '3', '4'] else result[4]
        else:
            diet_type = result[4]

        print("What chronic illnesses do you have? Current: ", result[5])
        print("1. Diabetes 2. Obesity 3. High blood pressure 4. Heart diseases 5. Lactose intolerance/food allergies 6. None")
        chronic_illness_choices = input("Enter new choices (comma-separated) or press Enter to keep current: ").split(',')
        illness_map = ['Diabetes', 'Obesity', 'High blood pressure', 'Heart diseases', 'Lactose intolerance/food allergies', 'None']
        
        if chronic_illness_choices:
            try:
                chronic_illnesses = [illness_map[int(choice.strip()) - 1] for choice in chronic_illness_choices]
            except (IndexError, ValueError):
                print("Invalid choice(s). Defaulting to 'None'.")
                chronic_illnesses = ['None']
        else:
            chronic_illnesses = result[5].split(',')  # Keep current values

        print("What specific dietary restrictions do you follow? Current: ", result[6])
        print("1. Low-sugar 2. Low-fat 3. Low-salt 4. Protein-rich 5. Anti-inflammatory 6. Gluten-free")
        dietary_restriction_choices = input("Enter new choices (comma-separated) or press Enter to keep current: ").split(',')
        restriction_map = ['Low-sugar', 'Low-fat', 'Low-salt', 'Protein-rich', 'Anti-inflammatory', 'Gluten-free']
        
        if dietary_restriction_choices:
            try:
                dietary_restrictions = [restriction_map[int(choice.strip()) - 1] for choice in dietary_restriction_choices]
            except (IndexError, ValueError):
                print("Invalid choice(s). No dietary restrictions recorded.")
                dietary_restrictions = []
        else:
            dietary_restrictions = result[6].split(',')  # Keep current values

        print("Are there specific ingredients that trigger your condition(s)? Current: ", result[7])
        print("1. Sugar 2. Fats 3. Salt 4. Lactose 5. Wheat 6. None")
        trigger_choices = input("Enter new choices (comma-separated) or press Enter to keep current: ").split(',')
        
        # Define the mapping including 'None'
        trigger_map = ['Sugar', 'Fats', 'Salt', 'Lactose', 'Wheat', 'None']
        
        if trigger_choices:
            try:
                trigger_ingredients = [trigger_map[int(choice.strip()) - 1] for choice in trigger_choices]
                if 'None' in trigger_ingredients:
                    trigger_ingredients = ['None']
            except (IndexError, ValueError):
                print("Invalid choice(s). No trigger ingredients recorded.")
                trigger_ingredients = []
        else:
            trigger_ingredients = result[7].split(',')  # Keep current values

        print("What health goal do you have? Current: ", result[8])
        print("1. Blood sugar control 2. Weight maintenance 3. Manage cholesterol 4. Blood pressure control 5. Bodybuilding 6. Control symptoms of your chronic illness 7. None")
        health_goal_choices = input("Enter new choices (comma-separated) or press Enter to keep current: ").split(',')
        goal_map = ['Blood sugar control', 'Weight maintenance', 'Manage cholesterol', 'Blood pressure control', 'Bodybuilding', 'Control symptoms of your chronic illness', 'None']
        
        if health_goal_choices:
            try:
                health_goals = [goal_map[int(choice.strip()) - 1] for choice in health_goal_choices]
            except (IndexError, ValueError):
                print("Invalid choice(s). Defaulting to 'None'.")
                health_goals = ['None']
        else:
            health_goals = result[8].split(',')  # Keep current values

        # Update the database with new values (if any were provided)
        cursor.execute('''UPDATE health_form 
                          SET age = ?, height = ?, weight = ?, diet_type = ?, 
                              chronic_illnesses = ?, dietary_restrictions = ?, 
                              trigger_ingredients = ?, health_goals = ?
                          WHERE username = ?''',
                       (age or result[2],
                        height or result[3], 
                        weight or result[4], 
                        diet_type,
                        ','.join(chronic_illnesses), 
                        ','.join(dietary_restrictions), 
                        ','.join(trigger_ingredients), 
                        ','.join(health_goals), 
                        username))

        conn.commit()
        print("Profile updated successfully.")
    else:
        print("User profile data not found.")
    conn.close()

@app.route('/edit_user_questions', methods=['GET', 'POST'])
def edit_user_questions():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = sqlite3.connect(HEALTH_DB_PATH)
    cursor = conn.cursor()

    if request.method == 'POST':
        # Retrieve and update user questions
        age = request.form.get('age')
        height = request.form.get('height')
        weight = request.form.get('weight')
        diet_type = request.form.get('diet_type')
        chronic_illnesses = request.form.get('chronic_illnesses')
        dietary_restrictions = request.form.get('dietary_restrictions')
        trigger_ingredients = request.form.get('trigger_ingredients')
        health_goals = request.form.get('health_goals')

        cursor.execute('''UPDATE health_form 
                          SET age = ?, height = ?, weight = ?, diet_type = ?, 
                              chronic_illnesses = ?, dietary_restrictions = ?, 
                              trigger_ingredients = ?, health_goals = ? 
                          WHERE username = ?''',
                       (age, height, weight, diet_type,
                        chronic_illnesses, dietary_restrictions,
                        trigger_ingredients, health_goals, username))

        conn.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('view_user_questions'))

    # Fetch current user data for the GET request
    cursor.execute("SELECT * FROM health_form WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return render_template('edit_user_questions.html', data=result)
    else:
        flash("User profile data not found.", "error")
        return redirect(url_for('view_profile'))






def change_password(username):
    """Change the user's password with old password verification."""
    db_path = os.path.join(os.path.dirname(__file__), 'user_auth.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Attempting to change password for username: {username}")

    old_password = getpass("Enter old password: ")
    new_password = getpass("Enter new password: ")
    confirm_password = getpass("Confirm new password: ")

    if new_password != confirm_password:
        print("Passwords do not match. Please try again.")
        conn.close()
        return

    hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
    cursor.execute("SELECT password FROM Users WHERE username = ?", (username,))
    stored_password = cursor.fetchone()

    if stored_password and stored_password[0] == hashed_old_password:
        hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
        cursor.execute("UPDATE Users SET password = ? WHERE username = ?", (hashed_new_password, username))
        conn.commit()
        print("Password updated successfully.")
    else:
        print("Old password is incorrect.")
    
    conn.close()

# Route for changing password
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
            return render_template('change_password.html')


        db_path = os.path.join(os.path.dirname(__file__), 'user_auth.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
        cursor.execute("SELECT password FROM Users WHERE username = ?", (username,))
        stored_password = cursor.fetchone()

        if stored_password and stored_password[0] == hashed_old_password:
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
            cursor.execute("UPDATE Users SET password = ? WHERE username = ?", (hashed_new_password, username))
            conn.commit()
            flash("Password updated successfully.", "success")
            conn.close()
            return redirect(url_for('view_profile'))
        else:
            flash("Old password is incorrect.", "error")

        conn.close()

    return render_template('change_password.html')


def log_out():
    """Handle the logout process with confirmation."""
    confirmation = input("Are you sure you want to log out? (yes/no): ").lower()
    if confirmation == "yes":
        print("Logging out...")
        return True  # Indicate successful logout
    else:
        print("Logout canceled.")
        return False  # Indicate logout was canceled

def change_account_info(username):
    """Change the user's account info (username or phone number)."""
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'user_auth.db'))
    cursor = conn.cursor()

    print("\n--- Change Account Info ---")
    print("1: Change Username")
    print("2: Change Phone Number")

    try:
        choice = int(input("Select an option: "))
        if choice == 1:
            email = input("Enter your email: ")
            password = getpass("Enter your password: ")
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute("SELECT * FROM Users WHERE username = ? AND email = ? AND password = ?", 
                           (username, email, hashed_password))
            result = cursor.fetchone()

            if result:
                new_username = input("Enter new username (alphanumeric): ")
                if new_username.isalnum():
                    cursor.execute("SELECT * FROM Users WHERE username = ?", (new_username,))
                    if cursor.fetchone():
                        print("Username already taken. Please try a different username.")
                    else:
                        cursor.execute("UPDATE Users SET username = ? WHERE email = ?", (new_username, email))
                        conn.commit()
                        print("Username updated successfully.")
                else:
                    print("Invalid username. Please enter alphanumeric characters only.")
            else:
                print("Authentication failed. Invalid email or password.")
        elif choice == 2:
            password = getpass("Enter your password: ")
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", 
                           (username, hashed_password))
            result = cursor.fetchone()

            if result:
                new_phone = input("Enter new phone number: ")
                cursor.execute("UPDATE Users SET phone_number = ? WHERE username = ?", (new_phone, username))
                conn.commit()
                print("Phone number updated successfully.")
            else:
                print("Authentication failed. Invalid username or password.")
        else:
            print("Invalid option. Please select a valid option.")
    except ValueError:
        print("Invalid input. Please enter a number.")
    conn.close()



@app.route('/change_account_info', methods=['GET', 'POST'])
def change_account_info():
    if request.method == 'POST':
        option = request.form.get('option')
        if option == 'change_username':
            return render_template('change_account_info.html', show_username_form=True)
        elif option == 'change_phone_number':
            return render_template('change_account_info.html', show_phone_form=True)
        else:
            flash("Invalid option selected.", "error")
    return render_template('change_account_info.html')

@app.route('/process_change', methods=['POST'])
def process_change():
    form_type = request.form.get('form_type')
    if form_type == 'username':
        return change_username()
    elif form_type == 'phone_number':
        return change_phone_number()
    else:
        flash("Invalid form type.", "error")
        return redirect(url_for('change_account_info'))

def change_username():
    email = request.form.get('email')
    password = request.form.get('password')
    new_username = request.form.get('new_username')

    if not email or not password or not new_username:
        flash("All fields are required.", "error")
        return redirect(url_for('change_account_info'))

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect('user_auth.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Users WHERE email = ? AND password = ?", (email, hashed_password))
    user = cursor.fetchone()

    if user:
        if new_username.isalnum():
            cursor.execute("SELECT * FROM Users WHERE username = ?", (new_username,))
            if cursor.fetchone():
                flash("Username already taken.", "error")
            else:
                cursor.execute("UPDATE Users SET username = ? WHERE email = ?", (new_username, email))
                conn.commit()
                flash("Username updated successfully.", "success")
        else:
            flash("Invalid username. Please enter alphanumeric characters only.", "error")
    else:
        flash("Authentication failed. Invalid email or password.", "error")

    conn.close()
    return redirect(url_for('change_account_info'))

def change_phone_number():
    username = request.form.get('username')
    password = request.form.get('password')
    new_phone = request.form.get('new_phone')

    if not username or not password or not new_phone:
        flash("All fields are required.", "error")
        return redirect(url_for('change_account_info'))

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect('user_auth.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()

    if user:
        cursor.execute("UPDATE Users SET phone_number = ? WHERE username = ?", (new_phone, username))
        conn.commit()
        flash("Phone number updated successfully.", "success")
    else:
        flash("Authentication failed. Invalid username or password.", "error")

    conn.close()
    return redirect(url_for('change_account_info'))




def view_auth_db():
    """Display all users in the authentication database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, phone_number, registration_date FROM Users")
    users = cursor.fetchall()
    
    print("\n--- Registered Users ---")
    for user in users:
        print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Phone: {user[3]}, Registration Date: {user[4]}")
    
    conn.close()

@app.route('/view_auth_db')
def view_auth_db():
    """Display all users in the authentication database."""
    conn = None
    users = []
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, phone_number, registration_date FROM Users")
        users = cursor.fetchall()
    except sqlite3.Error as e:
        flash(f"An error occurred: {e}", "error")
    finally:
        if conn:
            conn.close()
    
    return render_template('view_auth_db.html', users=users)




@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'username' in session and session['username'] == 'admin':
        if request.method == 'POST':
            form_data = {
                'username': request.form['username'],
                'password': request.form['password'],
                'email': request.form['email'],
                'phone_number': request.form.get('phone_number', '')
            }

            # Use the Register class to add a new user
            user_registration = Register(form_data)
            registration_result = user_registration.register_user()

            if registration_result:
                return "User added successfully!"
            else:
                return "Failed to add user. Please try again."
        return render_template('add_user.html')
    else:
        return redirect(url_for('login'))
    


@app.route('/remove_user', methods=['GET', 'POST'])
def remove_user():
    if 'username' in session and session['username'] == 'admin':  # Restrict access to admin
        if request.method == 'POST':
            username = request.form['username']

            if username == 'admin':
                return "The 'admin' account cannot be removed."

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if user:
                cursor.execute("DELETE FROM Users WHERE username = ?", (username,))
                conn.commit()
                conn.close()
                return "User removed successfully."
            else:
                conn.close()
                return "User not found."
        return render_template('remove_user.html')
    else:
        return redirect(url_for('login'))


@app.route('/change_user_password', methods=['GET', 'POST'])
def change_user_password():
    if 'username' in session and session['username'] == 'admin':  # Restrict to admin users
        if request.method == 'POST':
            username = request.form['username']

            if username == 'admin':
                return "The password for the 'admin' account cannot be changed."

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if user:
                new_password = request.form['new_password']
                confirm_password = request.form['confirm_password']

                if new_password == confirm_password:
                    hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                    cursor.execute("UPDATE Users SET password = ? WHERE username = ?", (hashed_password, username))
                    conn.commit()
                    conn.close()
                    return "Password updated successfully."
                else:
                    return "Passwords do not match."
            else:
                conn.close()
                return "User not found."
        return render_template('change_user_password.html')
    else:
        return redirect(url_for('login'))


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'username' in session and session['username'] == 'admin':  # Restrict to admin users
        if request.method == 'POST':
            barcode_num = request.form['barcode_num']
            if len(barcode_num) != 13:
                return "Invalid barcode number. Please enter a valid 13-digit barcode."

            product_name = request.form['product_name']
            ingredients = request.form['ingredients']
            try:
                energy = float(request.form['energy']) * 4.184  # Convert to kJ
                proteins = float(request.form['proteins'])
                carbohydrates = float(request.form['carbohydrates'])
                cholesterol = float(request.form['cholesterol'])
                sugars = float(request.form['sugars'])
                total_fat = float(request.form['total_fat'])
                saturated_fat = float(request.form['saturated_fat'])
                trans_fat = float(request.form['trans_fat'])
                sodium = float(request.form['sodium'])
                fruits_vegetables_nuts = float(request.form['fruits_vegetables_nuts'])
                dietary_fibre = float(request.form['dietary_fibre'])
                allergens = request.form['allergens']
                moist = request.form['moist']
            except ValueError:
                return "Invalid input for numeric values."

            # Nutri-Score calculation
            data = {
                'energy': energy,
                'fibers': dietary_fibre,
                'fruit_percentage': fruits_vegetables_nuts,
                'proteins': proteins,
                'saturated_fats': saturated_fat,
                'sodium': sodium,
                'sugar': sugars
            }
            nutri_score = calculate_nutri_score(data, moist)

            # Additional nutrients
            additional_minerals = {
                'calcium': request.form.get('calcium', 0),
                'iodine': request.form.get('iodine', 0),
                'zinc': request.form.get('zinc', 0),
                'phosphorous': request.form.get('phosphorous', 0),
                'magnesium': request.form.get('magnesium', 0)
            }
            additional_vitamins = {
                'vitamin_A': request.form.get('vitamin_A', 0),
                'vitamin_B': request.form.get('vitamin_B', 0),
                'vitamin_C': request.form.get('vitamin_C', 0),
                'vitamin_D': request.form.get('vitamin_D', 0),
                'vitamin_E': request.form.get('vitamin_E', 0),
                'vitamin_K': request.form.get('vitamin_K', 0)
            }
            additional_others = request.form.get('other', '')

            # Insert product into the database
            conn = sqlite3.connect(PRODUCT_DB_PATH)
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO Products (
                        barcode_num, product_name, ingredients, energy, proteins, carbohydrates, cholesterol,
                        sugars, total_fat, saturated_fat, trans_fat, sodium, fruits_vegetables_nuts, dietary_fibre,
                        allergens, nutrition_grade, calcium, iodine, zinc, phosphorous, magnesium,
                        vitamin_A, vitamin_B, vitamin_C, vitamin_D, vitamin_E, vitamin_K, other
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    barcode_num, product_name, ingredients, energy, proteins, carbohydrates, cholesterol,
                    sugars, total_fat, saturated_fat, trans_fat, sodium, fruits_vegetables_nuts, dietary_fibre,
                    allergens, nutri_score, additional_minerals['calcium'], additional_minerals['iodine'],
                    additional_minerals['zinc'], additional_minerals['phosphorous'], additional_minerals['magnesium'],
                    additional_vitamins['vitamin_A'], additional_vitamins['vitamin_B'], additional_vitamins['vitamin_C'],
                    additional_vitamins['vitamin_D'], additional_vitamins['vitamin_E'], additional_vitamins['vitamin_K'], additional_others
                ))
                conn.commit()
                return f"Product '{product_name}' added successfully with Nutri-Score: {nutri_score}."
            except sqlite3.IntegrityError:
                return "Error: Product with this barcode already exists."
            except sqlite3.Error as e:
                return f"Database error: {e}"
            finally:
                conn.close()

        return render_template('add_product.html')
    else:
        return redirect(url_for('login'))
    


# Route for deleting a product
@app.route('/delete_product', methods=['GET', 'POST'])
def delete_product():
    if request.method == 'POST':
        conn = sqlite3.connect(PRODUCT_DB_PATH)
        cursor = conn.cursor()

        # Get delete method from form submission
        delete_method = request.form.get('delete_method')

        if delete_method == "name":
            product_name = request.form.get('product_name')
            cursor.execute("DELETE FROM Products WHERE product_name = ?", (product_name,))
        elif delete_method == "barcode":
            barcode_num = request.form.get('barcode_num')
            cursor.execute("DELETE FROM Products WHERE barcode_num = ?", (barcode_num,))
        else:
            conn.close()
            return "Invalid option."

        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return f"Product deleted successfully."
        else:
            conn.close()
            return "No product found with the given information."

    return render_template('delete_product.html')

# @app.route('/view_all_products')
# def view_all_products():
#     conn = sqlite3.connect(PRODUCT_DB_PATH)
#     cursor = conn.cursor()
    
#     try:
#         cursor.execute("SELECT * FROM Products")
#         products = cursor.fetchall()
#     except sqlite3.Error as e:
#         print("Database error:", e)
#         products = []
#     finally:
#         conn.close()
    
#     return render_template('products.html', products=products)


from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler



# @app.route('/view_all_products')
# def view_all_products():
#     conn = sqlite3.connect(PRODUCT_DB_PATH)
#     cursor = conn.cursor()

#     try:
#         # Fetch product data
#         query = "SELECT * FROM Products"
#         df = pd.read_sql_query(query, conn)
        
#         # Perform clustering analysis
#         def map_nutrition_grade_to_numeric(grade):
#             """
#             Convert nutrition grade (A-E) to numeric values for clustering.
#             """
#             grade_mapping = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
#             return grade_mapping.get(grade, 5)  # Default to 5 for unknown grades
        
#         # Map nutrition grade to numeric
#         df['nutrition_grade_numeric'] = df['nutrition_grade'].map(map_nutrition_grade_to_numeric)
        
#         features = ['sugars', 'sodium', 'total_fat', 'saturated_fat', 'trans_fat', 
#                     'energy', 'proteins', 'cholesterol', 'carbohydrates', 'dietary_fibre']
        
#         # Normalize data for clustering
#         scaler = StandardScaler()
#         normalized_data = scaler.fit_transform(df[features].fillna(0))
        
#         # Apply K-Means clustering
#         kmeans = KMeans(n_clusters=3, init='k-means++', random_state=42)
#         df['Cluster'] = kmeans.fit_predict(normalized_data)
        
#         # Classify clusters into labels
#         cluster_labels = {0: 'Healthy', 1: 'Average', 2: 'Unhealthy'}  # Adjust based on actual cluster characteristics
#         df['Cluster_Label'] = df['Cluster'].map(cluster_labels)
        
#         # Prepare data for rendering
#         products = df.to_dict('records')  # Convert DataFrame to list of dictionaries for HTML rendering

#     except sqlite3.Error as e:
#         print("Database error:", e)
#         products = []
#     finally:
#         conn.close()

#     return render_template('products.html', products=products)

# @app.route('/view_all_products')
# def view_all_products():
#     conn = sqlite3.connect(PRODUCT_DB_PATH)
#     try:
#         # Fetch product data
#         query = "SELECT * FROM Products"
#         df = pd.read_sql_query(query, conn)

#         # Check if necessary columns are present
#         required_columns = ['sugars', 'sodium', 'total_fat', 'saturated_fat', 'trans_fat',
#                             'energy', 'proteins', 'cholesterol', 'carbohydrates', 'dietary_fibre', 'nutrition_grade']
#         missing_columns = [col for col in required_columns if col not in df.columns]
#         if missing_columns:
#             raise KeyError(f"Missing columns in the database: {missing_columns}")

#         # Convert nutrition grade to numeric for clustering
#         def map_nutrition_grade_to_numeric(grade):
#             grade_mapping = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
#             return grade_mapping.get(grade, 5)  # Default to 5 for unknown grades
        
#         df['nutrition_grade_numeric'] = df['nutrition_grade'].map(map_nutrition_grade_to_numeric)

#         # Normalize data for clustering
#         features = ['sugars', 'sodium', 'total_fat', 'saturated_fat', 'trans_fat',
#                     'energy', 'proteins', 'cholesterol', 'carbohydrates', 'dietary_fibre']
#         scaler = StandardScaler()
#         normalized_data = scaler.fit_transform(df[features].fillna(0))

#         # Apply K-Means clustering
#         kmeans = KMeans(n_clusters=3, init='k-means++', random_state=42)
#         df['Cluster'] = kmeans.fit_predict(normalized_data)

#         # Classify clusters into labels
#         cluster_labels = {0: 'Healthy', 1: 'Average', 2: 'Unhealthy'}
#         df['Cluster_Label'] = df['Cluster'].map(cluster_labels)

#         # Sort products by Cluster_Label: Healthy, Average, Unhealthy
#         cluster_order = ['Healthy', 'Average', 'Unhealthy']
#         df['Cluster_Label'] = pd.Categorical(df['Cluster_Label'], categories=cluster_order, ordered=True)
#         df = df.sort_values(by='Cluster_Label')

#         # Prepare data for rendering
#         products = df.to_dict('records')  # Convert DataFrame to list of dictionaries

#     except sqlite3.Error as e:
#         print("Database error:", e)
#         products = []
#     except KeyError as ke:
#         print("Data error:", ke)
#         products = []
#     finally:
#         conn.close()

#     return render_template('products.html', products=products)






import sqlite3
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os


def fetch_product_data(db_path):
    """
    Fetch product data from the database and return as a pandas DataFrame.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM Products"
        df = pd.read_sql_query(query, conn)
        return df
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def map_nutrition_grade_to_numeric(grade):
    """
    Convert nutrition grade (A-E) to numeric values for clustering.
    """
    grade_mapping = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    return grade_mapping.get(grade, 5)  # Default to 5 for unknown grades</p>

def cluster_products(df, n_clusters=3):
    """
    Cluster products based on nutritional information, including nutrition grade.
    """

    # Include nutrition grade as a feature for clustering
    df['nutrition_grade_numeric'] = df['nutrition_grade'].apply(map_nutrition_grade_to_numeric)

    features = ['sugars', 'sodium', 'total_fat', 'saturated_fat', 'trans_fat', 'energy', 'proteins',
                'cholesterol', 'carbohydrates', 'dietary_fibre', 'nutrition_grade_numeric']

    # Ensure the DataFrame contains the necessary columns
    missing_columns = [col for col in features if col not in df.columns]
    if missing_columns:
        raise KeyError(f"Missing columns in the DataFrame: {missing_columns}")

    # Handle missing values
    data = df[features].fillna(0)

    # Normalize features
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(data)

    # Tune the weight of the nutrition_grade_numeric feature to ensure it's significant but balanced
    nutrition_grade_index = features.index('nutrition_grade_numeric')
    normalized_data[:, nutrition_grade_index] *= 5  # Adjust multiplier if needed

    # Apply K-Means clustering with 'k-means++' initialization
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=42)
    df['Cluster'] = kmeans.fit_predict(normalized_data)

    return df, kmeans

def classify_using_clusters(df, cluster_analysis):
    """
    Classify products into categories: Healthy, Average, and Unhealthy based on cluster analysis.
    """
    # Determine classification based on cluster means
    # Example: Classify the cluster with the lowest mean nutrition_grade_numeric as Healthy
    cluster_means = cluster_analysis['nutrition_grade_numeric'].sort_values()
    cluster_labels = {
        cluster_means.index[0]: 'Healthy',
        cluster_means.index[1]: 'Average',
        cluster_means.index[2]: 'Unhealthy'
    }
    df['Cluster_Label'] = df['Cluster'].map(cluster_labels)
    return df

def analyze_clusters(df):
    """
    Analyze the characteristics of each cluster.
    """
    numeric_columns = ['sugars', 'sodium', 'total_fat', 'saturated_fat', 'trans_fat', 'energy', 'proteins',
                       'cholesterol', 'carbohydrates', 'dietary_fibre', 'nutrition_grade_numeric']

    # Ensure numeric columns are correctly typed
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Group by cluster and compute means
    cluster_analysis = df.groupby('Cluster')[numeric_columns].mean()
    
    return cluster_analysis

def classify_using_clusters(df):
    """
    Classify products into categories: Healthy, Average, and Unhealthy based on cluster analysis.
    """
    # Derive cluster labels from analysis rather than hard-coding
    # Update this mapping based on the analysis output
    cluster_labels = {0: 'Healthy', 1: 'Average', 2: 'Unhealthy'}  # Placeholder
    df['Cluster_Label'] = df['Cluster'].map(cluster_labels)
    return df

if __name__ == "__main__":
    db_path = "product_information.db"  # Path to your database
    df = fetch_product_data(db_path)

    if df is not None:
        try:
            # Step 1: Cluster products into 3 categories
            clustered_df, kmeans_model = cluster_products(df)

            # Step 2: Analyze clusters
            cluster_analysis = analyze_clusters(clustered_df)

            # Step 3: Classify products into health labels
            classified_df = classify_using_clusters(clustered_df)

            # Step 4: Display classified products with nutrition grade
            
            for _, row in classified_df.iterrows():
                print(f"{row['product_name']} -> {row['Cluster_Label']} (Cluster {row['Cluster']})")
        except Exception as e:
            print(f"Error in main workflow: {e}")


@app.route('/view_all_products')
def view_all_products():
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Fetch product data
        df = fetch_product_data(PRODUCT_DB_PATH)
        print("Fetched Data:")
        print(df.head())  # Debug: Print the first few rows of the fetched data
        
        # If no data is fetched, handle gracefully
        if df is None or df.empty:
            print("No products found in the database.")
            return render_template('products.html', products=[])

        # Perform clustering
        df, kmeans = cluster_products(df)
        print("Cluster Centers:")
        print(kmeans.cluster_centers_)  # Debug: Print the cluster centers

        # Map clusters to labels based on cluster means
        cluster_means = df.groupby('Cluster')['nutrition_grade_numeric'].mean().sort_values()
        print("Cluster Means:")
        print(cluster_means)  # Debug: Print mean nutrition grade for each cluster
        
        cluster_labels = {cluster: label for cluster, label in zip(
            cluster_means.index, ['Healthy', 'Average', 'Unhealthy'])}
        print("Cluster Labels Mapping:")
        print(cluster_labels)  # Debug: Print the mapping of clusters to labels

        # Assign cluster labels to products
        df['Cluster_Label'] = df['Cluster'].map(cluster_labels)
        print("Data with Cluster Labels:")
        print(df[['product_name', 'Cluster', 'Cluster_Label']].head())  # Debug: Print products with labels

        # Group products by their cluster labels
        healthy_products = df[df['Cluster_Label'] == 'Healthy'].to_dict('records')
        average_products = df[df['Cluster_Label'] == 'Average'].to_dict('records')
        unhealthy_products = df[df['Cluster_Label'] == 'Unhealthy'].to_dict('records')

    except sqlite3.Error as e:
        print("Database error:", e)
        healthy_products, average_products, unhealthy_products = [], [], []

    except Exception as e:
        print("Error in processing:", e)
        healthy_products, average_products, unhealthy_products = [], [], []

    finally:
        conn.close()
    print("Healthy Products:", healthy_products)
    print("Average Products:", average_products)
    print("Unhealthy Products:", unhealthy_products)

    # Render the products.html template with grouped product data
    return render_template(
        'products.html',
        healthy_products=healthy_products,
        average_products=average_products,
        unhealthy_products=unhealthy_products
    )



@app.route('/logout')
def logout():
    # Clear the user session
    session.clear()
    return redirect(url_for('logout_confirmation'))

@app.route('/logout_confirmation', methods=['GET', 'POST'])
def logout_confirmation():
    if request.method == 'POST':
        if request.form.get('confirm') == 'yes':
            session.clear()  # Ensure session is cleared
            return redirect(url_for('login'))  
        else:
            return redirect(url_for('admin'))  

    return render_template('logout_confirmation.html')
    

def display_filters():
    print("\nSelect one or more filter options (comma-separated):")
    print("1. Low Carbohydrates")
    print("2. High Proteins")
    print("3. Low Sugars")
    print("4. Low Sodium (Salt)")
    print("5. Low Fat")
    print("6. Low Saturated Fat")
    print("7. Dairy-Free")
    print("8. Wheat-Free")
    print("9. Nut-Free")
    print("10. Soy-Free")
    print("11. Sulphite-Free")
    
    # Allow multiple options to be selected
    options = input("\nChoose filters by entering their numbers (comma-separated): ").strip().split(',')

    sugar_threshold = 5  # Low sugar threshold
    sodium_threshold = 0.1  # Low sodium threshold
    fat_threshold = 3  # Low fat threshold
    sat_fat_threshold = 1.5  # Low saturated fat threshold

    # Fetch all products from the database
    products = get_all_products()

    filtered_products = []

    for product in products:
        allergens = product[15].lower()  # Allergens are in the 16th column, stored in uppercase, so convert to lowercase
        match = True

        for option in options:
            option = option.strip()  # Remove any extra spaces

            # Apply filters based on user selection
            if option == '1' and product[6] > 10:  # Low Carbohydrates
                match = False
            elif option == '2' and product[5] <= 10:  # High Proteins
                match = False
            elif option == '3' and product[8] > sugar_threshold:  # Low Sugars
                match = False
            elif option == '4' and product[12] > sodium_threshold:  # Low Sodium
                match = False
            elif option == '5' and product[9] > fat_threshold:  # Low Fat
                match = False
            elif option == '6' and product[10] > sat_fat_threshold:  # Low Saturated Fat
                match = False
            elif option == '7' and 'milk' in allergens:  # Dairy-Free
                match = False
            elif option == '8' and 'wheat' in allergens:  # Wheat-Free
                match = False
            elif option == '9' and ('nut' in allergens or 'peanut' in allergens):  # Nut-Free
                match = False
            elif option == '10' and 'soya' in allergens:  # Soy-Free
                match = False
            elif option == '11' and 'sulphite' in allergens:  # Sulphite-Free
                match = False

        if match:
            filtered_products.append(product)
    
    # Display filtered products and their warnings based on nutritional thresholds
    if filtered_products:
        for prod in filtered_products:
            print("\n--- Product ---")
            print(f"Product Name: {prod[2]}")
            print(f"Barcode: {prod[1]}")
            display_product_warnings(prod)
    else:
        print("No products match your filter.")

def get_all_products():
    """Fetch all products from the database."""
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT  FROM Products")
        products = cursor.fetchall()
        return products
    except sqlite3.Error as e:
        print("Database error:", e)
        return []
    finally:
        conn.close()

def display_product_warnings(product):
    """Displays warnings based on nutritional values and includes nutrition grade."""
    sugars = product[8]
    sodium = product[12]
    proteins = product[5]
    energy_kcal = product[4]
    fats = product[9]
    saturated_fat = product[10]
    nutrition_grade = product[16]  # Nutrition Grade is in the 17th column

    print(f"\n📊 Nutrition Grade: {nutrition_grade}")

    if sugars > 22.5:
        print("\n⚠️ WARNING: This product is high in sugar!")
    elif sugars <= 5:
        print("\n🍎 NOTE: This product is low in sugar!")

    if sodium > 0.6:
        print("\n⚠️ WARNING: This product is high in sodium!")
    elif sodium <= 0.1:
        print("\n🥗 NOTE: This product is low in sodium!")

    if energy_kcal > 0:
        protein_energy_percentage = (proteins * 4 / energy_kcal) * 100
        if protein_energy_percentage >= 20:
            print("\n💪 NOTE: This product is high in protein!")

    if fats > 17.5:
        print("\n🍔 WARNING: This product is high in total fat!")
    elif fats < 0.5:
        print("\n🥬 NOTE: This product is fat-free!")
    elif fats < 3:
        print("\n🥗 NOTE: This product is low in fat!")

    if saturated_fat > 5:
        print("\n🥓 WARNING: This product is high in saturated fat!")
    elif saturated_fat < 0.1:
        print("\n🌱 NOTE: This product is free of saturated fat!")
    elif saturated_fat < 1.5:
        print("\n🥑 NOTE: This product is low in saturated fat!")




def get_all_products():
    """Fetch all products from the database."""
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM Products")  # Adjust the query to fetch all columns
        products = cursor.fetchall()
        return products
    except sqlite3.Error as e:
        print("Database error:", e)
        return []
    finally:
        conn.close()

@app.route('/filters', methods=['GET', 'POST'])
def filter_products():
    if request.method == 'POST':
        selected_filters = request.form.getlist('filters')
        products = get_all_products()
        filtered_products = apply_filters(products, selected_filters)

        # Prepare warnings for each filtered product
        products_with_warnings = []
        for product in filtered_products:
            warnings = display_product_warnings(product)
            products_with_warnings.append((product, warnings))

        return render_template('filter_results.html', products=products_with_warnings)

   

def apply_filters(products, selected_filters):
    """Apply filters to the list of products based on user selection."""
    sugar_threshold = 5  # Low sugar threshold
    sodium_threshold = 0.1  # Low sodium threshold
    fat_threshold = 3  # Low fat threshold
    sat_fat_threshold = 1.5  # Low saturated fat threshold

    filtered_products = []
    
    for product in products:
        allergens = product[15].lower()  # Allergens are in the 16th column, stored in uppercase
        match = True
        
        for option in selected_filters:
            option = option.strip()  # Remove any extra spaces

            # Apply filters based on user selection
            if option == '1' and product[6] > 10:  # Low Carbohydrates
                match = False
            elif option == '2' and product[5] <= 10:  # High Proteins
                match = False
            elif option == '3' and product[8] > sugar_threshold:  # Low Sugars
                match = False
            elif option == '4' and product[12] > sodium_threshold:  # Low Sodium
                match = False
            elif option == '5' and product[9] > fat_threshold:  # Low Fat
                match = False
            elif option == '6' and product[10] > sat_fat_threshold:  # Low Saturated Fat
                match = False
            elif option == '7' and 'milk' in allergens:  # Dairy-Free
                match = False
            elif option == '8' and 'wheat' in allergens:  # Wheat-Free
                match = False
            elif option == '9' and ('nut' in allergens or 'peanut' in allergens):  # Nut-Free
                match = False
            elif option == '10' and 'soya' in allergens:  # Soy-Free
                match = False
            elif option == '11' and 'sulphite' in allergens:  # Sulphite-Free
                match = False

        if match:
            filtered_products.append(product)

    return filtered_products

def display_product_warnings(product):
    """Displays warnings based on nutritional values and includes nutrition grade."""
    sugars = product[8]
    sodium = product[12]
    proteins = product[5]
    energy_kcal = product[4]
    fats = product[9]
    saturated_fat = product[10]
    nutrition_grade = product[16]  # Nutrition Grade is in the 17th column

    warnings = [f" Nutritional Grade: {nutrition_grade}"]

    if sugars > 22.5:
        warnings.append("⚠️ WARNING: This product is high in sugar!")
    elif sugars <= 5:
        warnings.append("🍎 NOTE: This product is low in sugar!")

    if sodium > 0.6:
        warnings.append("⚠️ WARNING: This product is high in sodium!")
    elif sodium <= 0.1:
        warnings.append("🥗 NOTE: This product is low in sodium!")

    if energy_kcal > 0:
        protein_energy_percentage = (proteins * 4 / energy_kcal) * 100
        if protein_energy_percentage >= 20:
            warnings.append("💪 NOTE: This product is high in protein!")

    if fats > 17.5:
        warnings.append("🍔 WARNING: This product is high in total fat!")
    elif fats < 0.5:
        warnings.append("🥬 NOTE: This product is fat-free!")
    elif fats < 3:
        warnings.append("🥗 NOTE: This product is low in fat!")

    if saturated_fat > 5:
        warnings.append("🥓 WARNING: This product is high in saturated fat!")
    elif saturated_fat < 0.1:
        warnings.append("🌱 NOTE: This product is free of saturated fat!")
    elif saturated_fat < 1.5:
        warnings.append("🥑 NOTE: This product is low in saturated fat!")

    return warnings



def get_product_by_id(product_id):
    # Connect to your product information database
    conn = sqlite3.connect('product_information.db')
    cursor = conn.cursor()

    # Query to fetch the product details by product_id
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    # Close the connection
    conn.close()

    return product


@app.route('/product/<int:product_id>')
def product_info(product_id):
    # Fetch product details from the database using product_id
    product = get_product_by_id(product_id)
    if product:
        return render_template('product_info.html', product=product)
    else:
        return "Product not found", 404



def get_product_by_name(product_name):
    # Connect to your database (update the database name as needed)
    conn = sqlite3.connect('product_information.db')
    cursor = conn.cursor()
    
    # Use parameterized query to prevent SQL injection
    cursor.execute("SELECT * FROM products WHERE product_name = ?", (product_name,))
    product = cursor.fetchone()  # Fetch one product that matches the name

    conn.close()  # Close the connection
    return product  # Return the product data, or None if not found

@app.route('/product/name/<string:product_name>')
def product_name(product_name):
    # Fetch product details from the database using product_name
    product = get_product_by_name(product_name)
    if product:
        return render_template('product_name.html', product=product)
    else:
        return "Product not found", 404



# def collect_form_data(username, form_data):
#     """Collect and store health data from the user."""
#     conn = sqlite3.connect(HEALTH_DB_PATH)
#     cursor = conn.cursor()

#     # Extract data from the form
#     age = int(form_data.get("age", 0))  # Default to 0 if not provided
#     height = float(form_data.get("height", 0.0))  # Default to 0.0 if not provided
#     weight = float(form_data.get("weight", 0.0))  # Default to 0.0 if not provided

#     diet_type = form_data.get("diet_type", '')
#     chronic_illnesses = form_data.getlist("chronic_illnesses")  # List of selected illnesses
#     dietary_restrictions = form_data.getlist("dietary_restrictions")  # List of selected restrictions
#     trigger_ingredients = form_data.getlist("trigger_ingredients")  # List of selected trigger ingredients
#     health_goals = form_data.getlist("health_goals")  # List of selected health goals

#     # Insert into database
#     cursor.execute('''INSERT INTO health_form (username, age, height, weight, diet_type, chronic_illnesses, dietary_restrictions, trigger_ingredients, health_goals)
#                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
#         username, age, height, weight, 
#         diet_type, 
#         ','.join(chronic_illnesses), 
#         ','.join(dietary_restrictions), 
#         ','.join(trigger_ingredients),
#         ','.join(health_goals)
#     ))

#     conn.commit()
#     conn.close()

#     return {
#         'What is your dietary type?': [diet_type],
#         'What chronic illnesses do you have? (separate multiple answers with commas)': chronic_illnesses,
#         'What specific dietary restrictions do you follow? (separate multiple answers with commas)': dietary_restrictions,
#         'Are there specific ingredients that trigger your condition(s) or cause discomfort? (separate multiple answers with commas)': trigger_ingredients,
#         'What health goal do you have? (separate multiple answers with commas)': health_goals
#     }

def edit_product():
    """Edit a product and its nutrient info in the database."""
    try:
        conn = sqlite3.connect(PRODUCT_DB_PATH)
        cursor = conn.cursor()

        # Get product to edit
        barcode_num = input("Enter product barcode number: ")
        cursor.execute("SELECT * FROM Products WHERE barcode_num = ?", (barcode_num,))
        product = cursor.fetchone()
        
        if not product:
            print("Product not found.")
            return

        # Display current product information
        columns = [description[0] for description in cursor.description]
        print("\nCurrent product information:")
        for i, value in enumerate(product):
            print(f"{columns[i]}: {value}")

        # Collect updated product details
        print("\nUpdating product information:")
        new_values = list(product)
        nutri_score_relevant_fields = ['energy', 'dietary_fibre', 'fruits_vegetables_nuts', 'proteins', 'saturated_fat', 'sodium', 'sugars']
        nutri_score_fields_changed = False

        for i, column in enumerate(columns[1:], start=1):  # Start from index 1 to skip barcode
            edit_column = input(f"Do you want to edit {column}? (yes/no): ").lower()
            if edit_column == 'yes':
                new_value = input(f"Enter new {column} ({product[i]}): ").strip()
                if new_value:
                    if column in ['energy', 'proteins', 'carbohydrates', 'cholesterol', 'sugars', 'total_fat', 'saturated_fat', 'trans_fat', 'sodium', 'fruits_vegetables_nuts', 'dietary_fibre', 'calcium', 'iodine', 'zinc', 'phosphorous', 'magnesium', 'vitamin_A', 'vitamin_B', 'vitamin_C', 'vitamin_D', 'vitamin_E', 'vitamin_K']:
                        new_values[i] = float(new_value)
                    else:
                        new_values[i] = new_value
                    if column in nutri_score_relevant_fields:
                        nutri_score_fields_changed = True

        # Calculate new Nutri-Score only if relevant fields were changed
        if nutri_score_fields_changed:
            moist = input("Enter product type (solid or beverage): ").strip().lower()
            data = {
                'energy': new_values[columns.index('energy')] * 4.184,
                'fibers': new_values[columns.index('dietary_fibre')],
                'fruit_percentage': new_values[columns.index('fruits_vegetables_nuts')],
                'proteins': new_values[columns.index('proteins')],
                'saturated_fats': new_values[columns.index('saturated_fat')],
                'sodium': new_values[columns.index('sodium')],
                'sugar': new_values[columns.index('sugars')]
            }
            new_values[columns.index('nutrition_grade')] = calculate_nutri_score(data, moist)
            print(f"New Nutri-Score calculated: {new_values[columns.index('nutrition_grade')]}")
        else:
            print("Nutri-Score relevant fields were not changed. Keeping the original Nutri-Score.")

        # Update the product in the database
        update_query = f"UPDATE Products SET {', '.join(f'{col} = ?' for col in columns[1:])} WHERE barcode_num = ?"
        cursor.execute(update_query, new_values[1:] + [barcode_num])
        conn.commit()
        print(f"Product '{new_values[1]}' updated successfully.")

        # Verify the update
        cursor.execute("SELECT * FROM Products WHERE barcode_num = ?", (barcode_num,))
        updated_product = cursor.fetchone()
        print("\nUpdated product information:")
        for i, value in enumerate(updated_product):
            print(f"{columns[i]}: {value}")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            



@app.route('/edit_product', methods=['GET', 'POST'])
def edit_product():
    if request.method == 'POST':
     
        barcode_num = request.form.get('barcode_num')
        new_values = {
            'energy': request.form.get('energy'),
            'dietary_fibre': request.form.get('dietary_fibre'),
            'fruits_vegetables_nuts': request.form.get('fruits_vegetables_nuts'),
            'proteins': request.form.get('proteins'),
            'saturated_fat': request.form.get('saturated_fat'),
            'sodium': request.form.get('sodium'),
            'sugars': request.form.get('sugars'),
            
        }

        try:
            conn = sqlite3.connect(PRODUCT_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Products WHERE barcode_num = ?", (barcode_num,))
            product = cursor.fetchone()

            if not product:
                return "Product not found", 404

            # Perform the update
            update_query = "UPDATE Products SET "
            update_query += ", ".join([f"{key} = ?" for key in new_values.keys()])
            update_query += " WHERE barcode_num = ?"
            cursor.execute(update_query, list(new_values.values()) + [barcode_num])
            conn.commit()
            message = f"Product '{barcode_num}' updated successfully."
            return render_template('edit_product.html', message=message)

        except sqlite3.Error as e:
            return f"An error occurred: {e}", 500
        finally:
            if conn:
                conn.close()
    else:
        return render_template('edit_product.html')




# def calculate_probabilities(user_input, data):
#     total_count = len(data)
#     ingredient_counts = defaultdict(int)
#     conditional_counts = defaultdict(lambda: defaultdict(int))

#     for _, row in data.iterrows():
#         ingredients_str = row['What are some healthy alternatives/ingredients you include in your diet?']
#         if pd.notna(ingredients_str) and isinstance(ingredients_str, str):
#             ingredients = [ing.strip().lower() for ing in ingredients_str.split(',')]
#             for ingredient in ingredients:
#                 ingredient_counts[ingredient] += 1
#                 for column, values in user_input.items():
#                     if pd.notna(row[column]):
#                         row_values = set(val.strip().lower() for val in str(row[column]).split(','))
#                         if any(value.lower() in row_values for value in values):
#                             conditional_counts[ingredient][column] += 1

#     probabilities = {}
#     smoothing_factor = 0.1  # Laplace smoothing
#     for ingredient, count in ingredient_counts.items():
#         prior = (count + smoothing_factor) / (total_count + smoothing_factor * len(ingredient_counts))
#         likelihood = 1
#         for column, values in user_input.items():
#             cond_count = conditional_counts[ingredient][column]
#             likelihood *= (cond_count + smoothing_factor) / (count + smoothing_factor * 2)
#         probabilities[ingredient] = prior * likelihood

#     return probabilities

# def recommend_ingredients(username):
#     # Fetch user data from the health database
#     user_input = fetch_health_data(username)

#     # Load the CSV file
#     df = pd.read_csv(REC_PRODUCT_PATH)
    
#     df.columns = [
#         'What is your dietary type?',
#         'What chronic illnesses do you have? (separate multiple answers with commas)',
#         'What specific dietary restrictions do you follow? (separate multiple answers with commas)',
#         'Are there specific ingredients that trigger your condition(s) or cause discomfort? (separate multiple answers with commas)',
#         'What are some healthy alternatives/ingredients you include in your diet?',
#         'What health goal do you have? (separate multiple answers with commas)'
#     ]

#     # Calculate probabilities
#     probabilities = calculate_probabilities(user_input, df)
    
#     # Sort ingredients by probability and filter those with confidence >= 0.010
#     recommended_ingredients = sorted(
#         [(ingredient, prob) for ingredient, prob in probabilities.items() if prob >= 0.010],
#         key=lambda x: x[1],
#         reverse=True
#     )

#     print("\nRecommended healthy alternatives/ingredients for your diet:")
#     if recommended_ingredients:
#         for i, (ingredient, _) in enumerate(recommended_ingredients, 1):
#             print(f"{i}. {ingredient.capitalize()}")
#     else:
#         print("No recommendations were found based on your input.")

#     # Ensure recommended_ingredients is a list and process each item
#     if isinstance(recommended_ingredients, tuple):
#         recommended_ingredients = list(recommended_ingredients)
#     elif not isinstance(recommended_ingredients, list):
#         recommended_ingredients = [recommended_ingredients]

#     # Process each ingredient
#     processed_ingredients = []
#     for item in recommended_ingredients:
#         # Split by numbers and periods, then take the last part
#         parts = re.split(r'\d+\.?\s*', item[0])  # Note: item[0] to get the ingredient name
#         ingredient = parts[-1].strip().lower() if parts else ''
#         if ingredient:
#             processed_ingredients.append(ingredient)

#     products = get_products_by_ingredients(processed_ingredients)

#     # Display product information
#     display_product_info_ing(products)

#     return None

# def fetch_health_data(username):
#     """Fetch health data from the database for a given user."""
#     conn = sqlite3.connect(HEALTH_DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute('''
#     SELECT age, height, weight, diet_type, chronic_illnesses, dietary_restrictions, trigger_ingredients, health_goals
#     FROM health_form
#     WHERE username = ?
#     ''', (username,))

#     result = cursor.fetchone()

#     if result:
#         # Map the fetched data to a dictionary similar to the form data
#         age, height, weight, diet_type, chronic_illnesses, dietary_restrictions, trigger_ingredients, health_goals,  = result
#         health_data = {
#             'What is your dietary type?': [diet_type],
#             'What chronic illnesses do you have? (separate multiple answers with commas)': chronic_illnesses.split(','),
#             'What specific dietary restrictions do you follow? (separate multiple answers with commas)': dietary_restrictions.split(','),
#             'Are there specific ingredients that trigger your condition(s) or cause discomfort? (separate multiple answers with commas)': trigger_ingredients.split(','),
#             'What health goal do you have? (separate multiple answers with commas)': health_goals.split(',')
#         }
#     else:
#         print(f"No data found for user {username}.")
#         health_data = {}

#     conn.close()

#     return health_data

# def get_products_by_ingredients(ingredients):
#     # Connect to the SQLite database
#     conn = sqlite3.connect(PRODUCT_DB_PATH)
#     cursor = conn.cursor()

#     try:
#         # Ensure ingredients is a list and remove any blank spaces
#         if isinstance(ingredients, tuple):
#             ingredients = list(ingredients)
#         elif not isinstance(ingredients, list):
#             ingredients = [ingredients]

#         # Remove blank spaces and empty strings from ingredients
#         ingredients = [i.strip().lower() for i in ingredients if i.strip()]

#         # Create a query that will match any of the ingredients
#         query = """
#         SELECT id, barcode_num, product_name, ingredients, energy, proteins, carbohydrates, cholesterol, sugars, total_fat, saturated_fat, trans_fat, sodium, fruits_vegetables_nuts, dietary_fibre, allergens, nutrition_grade, calcium, iodine, zinc, phosphorous, magnesium, vitamin_A, vitamin_B, vitamin_C, vitamin_D, vitamin_E, vitamin_K, other
#         FROM products
#         WHERE {}
#         """

#         # Create conditions for each ingredient
#         conditions = " OR ".join([f"LOWER(ingredients) LIKE ?" for _ in ingredients])
#         query = query.format(conditions)

#         # Execute the query with all ingredients
#         cursor.execute(query, tuple(f'%{ingredient}%' for ingredient in ingredients))

#         # Fetch all matching results
#         results = cursor.fetchall()
#         return results

#     except sqlite3.Error as e:
#         print(f"An error occurred: {e}")
#     finally:
#         # Close the database connection
#         conn.close()

#     return None

# def display_product_info_ing(products):
#     if not products:
#         print("No products found containing any of the recommended ingredients.")
#         return

#     for product in products:
#         print("\nProduct Information:")
#         print(f"Product Name: {product[2]}")
#         print(f"Barcode: {product[1]}")
#         print(f"Ingredients: {product[3]}")
#         print(f"Energy: {product[4]}")
#         print(f"Proteins: {product[5]}")
#         print(f"Carbohydrates: {product[6]}")
#         print(f"Cholesterol: {product[7]}")
#         print(f"Sugars: {product[8]}")
#         print(f"Total Fat: {product[9]}")
#         print(f"Saturated Fat: {product[10]}")
#         print(f"Trans Fat: {product[11]}")
#         print(f"Sodium: {product[12]}")
#         print(f"Fruits/Vegetables/Nuts: {product[13]}")
#         print(f"Dietary Fibre: {product[14]}")
#         print(f"Allergens: {product[15]}")
#         print(f"Nutrition Grade: {product[16]}")
#         print(f"Calcium: {product[17]}")
#         print(f"Iodine: {product[18]}")
#         print(f"Zinc: {product[19]}")
#         print(f"Phosphorous: {product[20]}")
#         print(f"Magnesium: {product[21]}")
#         print(f"Vitamin A: {product[22]}")
#         print(f"Vitamin B: {product[23]}")
#         print(f"Vitamin C: {product[24]}")
#         print(f"Vitamin D: {product[25]}")
#         print(f"Vitamin E: {product[26]}")
#         print(f"Vitamin K: {product[27]}")
#         print(f"Other: {product[28]}")
#         print("-" * 50) 




# @app.route('/recommend', methods=['GET', 'POST'])
# def recommend():
#     if request.method == 'POST':
#         # Assuming the user is logged in and their username is stored in session
#         username = session.get('username')
#         if not username:
#             return redirect(url_for('login'))  # Redirect to login if user is not logged in

#         # Collect form data and generate recommendations
#         form_data = fetch_health_data(username)
#         recommended_ingredients = recommend_ingredients(username)

#         # Fetch products that contain the recommended ingredients
#         recommended_products = get_products_by_ingredients(recommended_ingredients)

#         # Render the recommendation results on the HTML page
#         return render_template('recommendations.html', 
#                                recommendations=recommended_ingredients, 
#                                recommended_products=recommended_products)
    
#     # Render the form to collect user health data
#     return render_template('health_form.html')


# def fetch_health_data(username):
#     """Fetch health data from the database for a given user."""
#     conn = sqlite3.connect(HEALTH_DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute('''
#     SELECT age, height, weight, diet_type, chronic_illnesses, dietary_restrictions, trigger_ingredients, health_goals
#     FROM health_form
#     WHERE username = ?
#     ''', (username,))

#     result = cursor.fetchone()

#     if result:
#         # Map the fetched data to a dictionary similar to the form data
#         age, height, weight, diet_type, chronic_illnesses, dietary_restrictions, trigger_ingredients, health_goals = result
#         health_data = {
#             'What is your dietary type?': [diet_type],
#             'What chronic illnesses do you have? (separate multiple answers with commas)': chronic_illnesses.split(','),
#             'What specific dietary restrictions do you follow? (separate multiple answers with commas)': dietary_restrictions.split(','),
#             'Are there specific ingredients that trigger your condition(s) or cause discomfort? (separate multiple answers with commas)': trigger_ingredients.split(','),
#             'What health goal do you have? (separate multiple answers with commas)': health_goals.split(',')
#         }
#     else:
#         print(f"No data found for user {username}.")
#         health_data = {}

#     conn.close()
#     return health_data


# def recommend_ingredients(username):
#     # Fetch user data from the health database
#     user_input = fetch_health_data(username)

#     # Load the CSV file
#     df = pd.read_csv('rec_file.csv')
    
#     df.columns = [
#         'What is your dietary type?',
#         'What chronic illnesses do you have? (separate multiple answers with commas)',
#         'What specific dietary restrictions do you follow? (separate multiple answers with commas)',
#         'Are there specific ingredients that trigger your condition(s) or cause discomfort? (separate multiple answers with commas)',
#         'What are some healthy alternatives/ingredients you include in your diet?',
#         'What health goal do you have? (separate multiple answers with commas)'
#     ]

#     # Calculate probabilities
#     probabilities = calculate_probabilities(user_input, df)
    
#     # Sort ingredients by probability and filter those with confidence >= 0.010
#     recommended_ingredients = sorted(
#         [(ingredient, prob) for ingredient, prob in probabilities.items() if prob >= 0.000001],
#         key=lambda x: x[1],
#         reverse=True
#     )

#     # Return only the ingredients (without probabilities) for rendering in the HTML
#     return [ingredient.capitalize() for ingredient, _ in recommended_ingredients]

# def calculate_probabilities(user_input, data):
#     total_count = len(data)
#     ingredient_counts = defaultdict(int)
#     conditional_counts = defaultdict(lambda: defaultdict(int))

#     for _, row in data.iterrows():
#         ingredients_str = row['What are some healthy alternatives/ingredients you include in your diet?']
#         if pd.notna(ingredients_str) and isinstance(ingredients_str, str):
#             ingredients = [ing.strip().lower() for ing in ingredients_str.split(',')]
#             for ingredient in ingredients:
#                 ingredient_counts[ingredient] += 1
#                 for column, values in user_input.items():
#                     if pd.notna(row[column]):
#                         row_values = set(val.strip().lower() for val in str(row[column]).split(','))
#                         if any(value.lower() in row_values for value in values):
#                             conditional_counts[ingredient][column] += 1

#     probabilities = {}
#     smoothing_factor = 0.1  # Laplace smoothing
#     for ingredient, count in ingredient_counts.items():
#         prior = (count + smoothing_factor) / (total_count + smoothing_factor * len(ingredient_counts))
#         likelihood = 1
#         for column, values in user_input.items():
#             cond_count = conditional_counts[ingredient][column]
#             likelihood *= (cond_count + smoothing_factor) / (count + smoothing_factor * 2)
#         probabilities[ingredient] = prior * likelihood

#     return probabilities

# def get_products_by_ingredients(ingredients):
#     """Fetch products from the database containing any of the recommended ingredients."""
#     # Connect to the SQLite database
#     conn = sqlite3.connect(PRODUCT_DB_PATH)
#     cursor = conn.cursor()

#     try:
#         # Ensure ingredients is a list and remove any blank spaces
#         if isinstance(ingredients, tuple):
#             ingredients = list(ingredients)
#         elif not isinstance(ingredients, list):
#             ingredients = [ingredients]

#         # Remove blank spaces and empty strings from ingredients
#         ingredients = [i.strip().lower() for i in ingredients if i.strip()]

#         # Create a query that will match any of the ingredients
#         query = """
#         SELECT id, barcode_num, product_name, ingredients, energy, proteins, carbohydrates, cholesterol, sugars, total_fat, saturated_fat, trans_fat, sodium, fruits_vegetables_nuts, dietary_fibre, allergens, nutrition_grade, calcium, iodine, zinc, phosphorous, magnesium, vitamin_A, vitamin_B, vitamin_C, vitamin_D, vitamin_E, vitamin_K, other
#         FROM products
#         WHERE {}
#         """

#         # Create conditions for each ingredient
#         conditions = " OR ".join([f"LOWER(ingredients) LIKE ?" for _ in ingredients])
#         query = query.format(conditions)

#         # Execute the query with all ingredients
#         cursor.execute(query, tuple(f'%{ingredient}%' for ingredient in ingredients))

#         # Fetch all matching results
#         results = cursor.fetchall()

#         # Transform the results into a list of dictionaries for easier template rendering
#         product_list = []
#         for product in results:
#             product_data = {
#                 'product_name': product[2],
#                 'barcode': product[1],
#                 'ingredients': product[3],
#                 'energy': product[4],
#                 'proteins': product[5],
#                 'carbohydrates': product[6],
#                 'cholesterol': product[7],
#                 'sugars': product[8],
#                 'total_fat': product[9],
#                 'saturated_fat': product[10],
#                 'trans_fat': product[11],
#                 'sodium': product[12],
#                 'fruits_vegetables_nuts': product[13],
#                 'dietary_fibre': product[14],
#                 'allergens': product[15],
#                 'nutrition_grade': product[16],
#                 'calcium': product[17],
#                 'iodine': product[18],
#                 'zinc': product[19],
#                 'phosphorous': product[20],
#                 'magnesium': product[21],
#                 'vitamin_A': product[22],
#                 'vitamin_B': product[23],
#                 'vitamin_C': product[24],
#                 'vitamin_D': product[25],
#                 'vitamin_E': product[26],
#                 'vitamin_K': product[27],
#                 'other': product[28],
#             }
#             product_list.append(product_data)

#         return product_list

#     except sqlite3.Error as e:
#         print(f"An error occurred: {e}")
#     finally:
#         # Close the database connection
#         conn.close()

#     return []



def fetch_health_data(username):

    """Fetch health data from the database for a given user."""

    conn = sqlite3.connect(HEALTH_DB_PATH)

    cursor = conn.cursor()

    cursor.execute('''

    SELECT age, height, weight, diet_type, chronic_illnesses, dietary_restrictions, trigger_ingredients, health_goals

    FROM health_form

    WHERE username = ?

    ''', (username,))

    result = cursor.fetchone()

    if result:

        # Map the fetched data to a dictionary similar to the form data

        age, height, weight, diet_type, chronic_illnesses, dietary_restrictions, trigger_ingredients, health_goals = result

        health_data = {

            'What is your dietary type?': diet_type.lower(),

            'What chronic illnesses do you have? ': ','.join([illness.strip().lower() for illness in chronic_illnesses.split(',') if illness]),

            'What specific dietary restrictions do you follow?': ','.join([restriction.strip().lower() for restriction in dietary_restrictions.split(',') if restriction]),

            'Are there specific ingredients that trigger your condition(s) or cause discomfort? ': ','.join([trigger.strip().lower() for trigger in trigger_ingredients.split(',') if trigger]),

            'What health goal do you have?': ','.join([goal.strip().lower() for goal in health_goals.split(',') if goal])

        }

    else:

        health_data = {}

    conn.close()

    return health_data


def display_product_info_ing(products):
    if not products:
        print("No products found containing any of the recommended ingredients.")
        return

    for product in products:
        print("\nProduct Information:")
        print(f"Product Name: {product[2]}")
        print(f"Barcode: {product[1]}")
        print(f"Ingredients: {product[3]}")
        print(f"Energy: {product[4]}")
        print(f"Proteins: {product[5]}")
        print(f"Carbohydrates: {product[6]}")
        print(f"Cholesterol: {product[7]}")
        print(f"Sugars: {product[8]}")
        print(f"Total Fat: {product[9]}")
        print(f"Saturated Fat: {product[10]}")
        print(f"Trans Fat: {product[11]}")
        print(f"Sodium: {product[12]}")
        print(f"Fruits/Vegetables/Nuts: {product[13]}")
        print(f"Dietary Fibre: {product[14]}")
        print(f"Allergens: {product[15]}")
        print(f"Nutrition Grade: {product[16]}")
        print(f"Calcium: {product[17]}")
        print(f"Iodine: {product[18]}")
        print(f"Zinc: {product[19]}")
        print(f"Phosphorous: {product[20]}")
        print(f"Magnesium: {product[21]}")
        print(f"Vitamin A: {product[22]}")
        print(f"Vitamin B: {product[23]}")
        print(f"Vitamin C: {product[24]}")
        print(f"Vitamin D: {product[25]}")
        print(f"Vitamin E: {product[26]}")
        print(f"Vitamin K: {product[27]}")
        print(f"Other: {product[28]}")
        print("-" * 50) 

from flask import Flask, request, render_template
import pandas as pd
import sqlite3
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split



# Initialize global variables
svm_pipeline, mlb, feature_cols = None, None, None

# Function to initialize the SVM model and feature columns
def initialize_model():
    global svm_pipeline, mlb, feature_cols

    # Load the dataset
    df = pd.read_csv('rec_file.csv')

    feature_cols = [
        'What is your dietary type?',
        'What chronic illnesses do you have? ',
        'What specific dietary restrictions do you follow?',
        'Are there specific ingredients that trigger your condition(s) or cause discomfort? ',
        'What health goal do you have?'
    ]

    target_col = 'What are some healthy alternatives/ingredients you include in your diet?'

    # Preprocess the target column for multi-label classification
    df[target_col] = df[target_col].fillna('').apply(lambda x: [item.strip().lower() for item in x.split(',') if item])

    # Fill missing values in features and transform to lowercase
    for col in feature_cols:
        df[col] = df[col].fillna('').astype(str).apply(lambda x: ','.join([item.strip().lower() for item in x.split(',') if item]))

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(df[feature_cols], df[target_col], test_size=0.2, random_state=42)

    # Transform target data using MultiLabelBinarizer for multi-label classification
    mlb = MultiLabelBinarizer()
    y_train_mlb = mlb.fit_transform(y_train)
    y_test_mlb = mlb.transform(y_test)

    # Define preprocessing for features
    preprocessor = ColumnTransformer(
        transformers=[
            (col, CountVectorizer(tokenizer=lambda x: x.split(','), lowercase=True, token_pattern=None), col)
            for col in feature_cols
        ],
        remainder='drop'
    )

    # Define the SVM model pipeline with OneVsRestClassifier
    svm_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('scaler', StandardScaler(with_mean=False)),
        ('clf', OneVsRestClassifier(SVC(kernel='linear', probability=True, random_state=42)))
    ])

    # Fit the model
    svm_pipeline.fit(X_train, y_train_mlb)

    # Return updated global variables
    return svm_pipeline, mlb, feature_cols

# Initialize the model globally
svm_pipeline, mlb, feature_cols = initialize_model()

def get_products_by_ingredients(ingredients):
    """Retrieve products based on ingredients."""
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()
    try:
        if not isinstance(ingredients, list):
            ingredients = [ingredients]
        # Clean and prepare ingredients
        ingredients = [i.strip().lower() for i in ingredients if i.strip()]
        if not ingredients:
            return []
        # Build the SQL query dynamically
        query = """
        SELECT id, barcode_num, product_name, ingredients, energy, proteins, carbohydrates,
               cholesterol, sugars, total_fat, saturated_fat, trans_fat, sodium,
               fruits_vegetables_nuts, dietary_fibre, allergens, nutrition_grade, calcium,
               iodine, zinc, phosphorous, magnesium, vitamin_A, vitamin_B, vitamin_C,
               vitamin_D, vitamin_E, vitamin_K, other
        FROM products
        WHERE {}
        """.format(" OR ".join([f"LOWER(ingredients) LIKE ?" for _ in ingredients]))
        # Execute the query
        cursor.execute(query, tuple(f"%{ingredient}%" for ingredient in ingredients))
        # Fetch and format results
        results = cursor.fetchall()
        if results:
            columns = [desc[0] for desc in cursor.description]
            products = [dict(zip(columns, row)) for row in results]
            return products
        return []
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        conn.close()


# Route to recommend ingredients based on user input
from flask import render_template

@app.route('/recommend_ingredients/<username>', methods=['GET', 'POST'])


# Function to initialize the SVM model globally
def recommend_ingredients(username, threshold=0.05):
 

    # Ensure 'username' is available

    if not username:

        return jsonify({"error": "'username' parameter is required."}), 400

    # Fetch the global model components

    global svm_pipeline, mlb, feature_cols

    # Ensure feature_cols is initialized

    if feature_cols is None:

        return jsonify({"error": "Model is not initialized. Please check the model configuration."}), 500

    # Retrieve and format user input as a DataFrame for prediction

    user_input = fetch_health_data(username)

    if not user_input:

        return jsonify({"error": f"No data found for user {username}."}), 404

    # Ensure input data is consistent with the format used during training

    input_df = pd.DataFrame([user_input], columns=feature_cols)

    for col in feature_cols:

        input_df[col] = input_df[col].fillna('').apply(lambda x: ','.join([item.strip().lower() for item in str(x).split(',') if item]))

    # Predict probabilities for each ingredient label using the trained model

    ingredient_probs = svm_pipeline.predict_proba(input_df)[0]

    # Collect ingredient recommendations based on the predicted probabilities

    ingredient_recommendations = [

        (ingredient, prob) for ingredient, prob in zip(mlb.classes_, ingredient_probs) if prob >= threshold

    ]

    # Sort recommendations by probability in descending order

    ingredient_recommendations.sort(key=lambda x: x[1], reverse=True)

    # Process the recommended ingredients for further use

    processed_ingredients = [ingredient.lower() for ingredient, _ in ingredient_recommendations]

    # Retrieve products based on the recommended ingredients

    products = get_products_by_ingredients(processed_ingredients)

    # Render the recommendations and products in the template

    

    return render_template('recommendations.html',

                           recommendations=[ingredient.capitalize() for ingredient, _ in ingredient_recommendations],

                           recommended_products=products)

svm_pipeline, mlb, feature_cols = initialize_model()



@app.route('/about_us')
def about_us():
    return render_template('about_us.html')












def menu():
    """Display the main menu and handle user input."""
    if not check_db_validity():
        print("Databases are not valid. Please fix the issues and try again.")
        return

    while True:
        print("\n--- Main Menu ---")
        print("0: Register")
        print("1: Log In")
        print("2: Quit Application")
        
        try:
            choice = int(input("Select an option: "))
            if choice == 0:
                fields = ["username", "password", "email", "phone_number"]
                reg = Register(*fields)
                reg.register_user()
            elif choice == 1:
                username = input("Enter username: ")
                password = getpass("Enter password: ")
                login = Login(username, password)
                login.authenticate()
            elif choice == 2:
                print("Quitting application.")
                break
            else:
                print("Invalid option. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number.")



import google.generativeai as genai
import os

# Set your Gemini API key here or through an environment variable
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBDN_NAZ-awHylUEJ3IF03PvcZQB9D1RlQ")

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Create the Gemini model instance
model = genai.GenerativeModel("gemini-2.0-flash")

# Broad list of loosely nutrition-related keywords
BROAD_KEYWORDS = [
    "nutrition", "calories", "healthy", "unhealthy", "sugar", "fat", "carbs", "protein",
    "fiber", "vitamin", "ingredient", "mineral", "sodium", "cholesterol", "diet", "vegan",
    "gluten", "organic", "preservative", "sweetener", "trans fat", "keto", "low carb", "junk food",
    "drink", "beverage", "snack", "dessert", "food", "eat", "eating", "meals", "fruit", "vegetable",
    "meat", "plant-based", "processed", "natural", "dairy", "milk", "soy", "oat", "peanut", "allergy",
    "health", "impact", "effect", "is it okay", "should I eat", "harmful", "benefits", "safe", "cancer",
    "risk", "gut", "digestion", "heart", "weight", "gain", "loss", "fitness", "sugar-free", "low sugar"
]

def is_broadly_nutrition_related(text: str) -> bool:
    """Accepts any broadly food/health-related input."""
    text = text.lower()
    return any(keyword in text for keyword in BROAD_KEYWORDS)

def get_gemini_response(user_input: str) -> str:
    """Handles food-related queries using Gemini, with broad filtering."""
    if not is_broadly_nutrition_related(user_input):
        return (
            "⚠️ I can only help with questions about food, nutrition, ingredients, or health.\n"
            "Try something like:\n"
            "- Is cupcakes healthy?\n"
            "- What does high fructose corn syrup do?\n"
            "- Can I have popcorn on a keto diet?"
        )

    try:
        response = model.generate_content(user_input)
        return response.text.strip() if response.text else "No response received."
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    print("🥗 Welcome to NutriBot — your food & ingredient health assistant!")
    print("💬 Ask me anything about food, nutrition, or health.\n(Type 'exit' to quit)\n")

    while True:
        user_input = input("🧠 You: ")

        if user_input.lower().strip() in ["exit", "quit", "bye"]:
            print("👋 NutriBot: Take care! Stay healthy and eat smart! 🥦")
            break

        response = get_gemini_response(user_input)
        print(f"🤖 NutriBot: {response}\n")

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import google.generativeai as genai
import os

app.secret_key = 'your_secret_key'

# 🔑 Configure Gemini API
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBDN_NAZ-awHylUEJ3IF03PvcZQB9D1RlQ")
genai.configure(api_key=GOOGLE_API_KEY)

# 🤖 Load Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

# 🔍 Keywords for filtering nutrition-related questions
BROAD_KEYWORDS = [
    "nutrition", "calories", "healthy", "unhealthy", "sugar", "fat", "carbs", "protein",
    "fiber", "vitamin", "ingredient", "mineral", "sodium", "cholesterol", "diet", "vegan",
    "gluten", "organic", "preservative", "sweetener", "trans fat", "keto", "low carb", "junk food",
    "drink", "beverage", "snack", "dessert", "food", "eat", "eating", "meals", "fruit", "vegetable",
    "meat", "plant-based", "processed", "natural", "dairy", "milk", "soy", "oat", "peanut", "allergy",
    "health", "impact", "effect", "is it okay", "should I eat", "harmful", "benefits", "safe", "cancer",
    "risk", "gut", "digestion", "heart", "weight", "gain", "loss", "fitness", "sugar-free", "low sugar"
]

# ✅ Check if input is nutrition-related
def is_broadly_nutrition_related(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in BROAD_KEYWORDS)

# 🤖 Send message to Gemini & get response
def get_gemini_response(user_input: str) -> str:
    if not is_broadly_nutrition_related(user_input):
        return (
            "⚠️ I can only help with questions about food, nutrition, ingredients, or health.\n"
            "Try asking:\n"
            "- Is cupcakes healthy?\n"
            "- What does high fructose corn syrup do?\n"
            "- Can I have popcorn on a keto diet?"
        )
    try:
        response = model.generate_content(user_input)
        return response.text.strip() if response.text else "No response received."
    except Exception as e:
        return f"Error: {str(e)}"

# 📩 Route to handle chat POST request from frontend
@app.route("/nutribot", methods=["POST"])
def nutribot():
    data = request.get_json()
    user_input = data.get("message", "")
    reply = get_gemini_response(user_input)
    return jsonify({"reply": reply})



        

if __name__ == "__main__":
 app.run(debug=True)
#  menu()  # Start the programs

