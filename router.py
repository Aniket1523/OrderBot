# Imports
import mysql.connector
from mysql.connector import pooling
from fastapi import APIRouter, HTTPException, Request

intermediate_orders = {}
router = APIRouter()

# Set up connection pool (ensure your db_config is correct)
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "*********",
    "database": "*********"
}

connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **db_config)


# Function to get a connection from the pool
def get_connection():
    return connection_pool.get_connection()


# Function to calculate total price of order
def calculate_order_total(order_details):
    total = 0
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch the price of each product based on its name
        for product_name, quantity in order_details.items():
            query = "SELECT Product_Price FROM products WHERE Product_Name = %s"
            cursor.execute(query, (product_name,))
            product = cursor.fetchone()

            if product:
                product_price = product['Product_Price']
                total += product_price * quantity
            else:
                raise HTTPException(status_code=400, detail=f"Product '{product_name}' not found.")

        return total
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating order total: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@router.post("/webhook")
async def dialogflow_webhook(request: Request):
    req = await request.json()

    # Extract the session ID to use as user_id
    session_id = req.get('session', '')
    user_id = session_id.split("/")[-1]  # Extract the last part of the session as user_id

    intent_name = req['queryResult']['intent']['displayName']
    parameters = req['queryResult']['parameters']

    # Route logic based on the intent
    if intent_name == "New Order Intent":
        return await handle_new_order(user_id)
    elif intent_name == "add to order":
        return await handle_add_to_order(parameters, user_id)
    elif intent_name == "Remove Item from order":
        return await handle_remove_from_order(parameters, user_id)
    elif intent_name == "Confirm Summary Order":
        return handle_confirm_order(user_id)
    elif intent_name == "Track Order Intent":  # Add this case
        return await handle_track_order(parameters, user_id)
    else:
        return {"fulfillmentText": "I'm sorry, I didn't understand that."}


async def handle_new_order(user_id):
    # Use user_id if needed (e.g., logging, associating data)
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = "SELECT Product_Name, Product_Price FROM products WHERE Stock > 0"
        cursor.execute(query)
        products = cursor.fetchall()

        if products:
            product_list = "\n".join(
                [f"{product['Product_Name']} - ₹{product['Product_Price']}\n" for product in products]
            )
            return {
                "fulfillmentText": f"Here are the products available for order:\n{product_list}\n\nPlease specify the product and quantity you would like to order."
            }
        else:
            return {"fulfillmentText": "Sorry, we currently have no products available for order."}
    except Exception as e:
        return {"fulfillmentText": f"An error occurred: {str(e)}"}
    finally:
        cursor.close()
        connection.close()


async def handle_add_to_order(parameters, user_id):
    global intermediate_orders

    # Extract product name(s) and quantity(ies) from parameters
    product_name = parameters.get("product_name", [])
    quantity = parameters.get("quantity", [])

    if not product_name or not quantity:
        raise HTTPException(status_code=400, detail="Product name or quantity is missing.")

    # Initialize or update the user's intermediate order
    if user_id not in intermediate_orders:
        intermediate_orders[user_id] = {}

    # Loop through each product and quantity
    for name, qty in zip(product_name, quantity):
        # Ensure the quantity is an integer and valid
        try:
            qty = int(qty)  # Ensure quantity is an integer
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid quantity value: {qty}")

        # Check if the product name is valid and store in the intermediate order
        if name.lower() in ['paint', 'fan', 'light', 'plywood']:
            if name in intermediate_orders[user_id]:
                intermediate_orders[user_id][name] += qty  # Add to existing quantity
            else:
                intermediate_orders[user_id][name] = qty  # Initialize the quantity

    # Prepare the order summary
    order_summary = "\n".join(
        [f"{item}: {qty}" for item, qty in intermediate_orders[user_id].items()]
    )
    total_cost = calculate_order_total(intermediate_orders[user_id])
    return {
        "fulfillmentText": f"Your current order:\n{order_summary}\nTotal: ₹{total_cost}\nDo you want to confirm your order or add/remove more items?"
    }


async def handle_remove_from_order(parameters, user_id):
    global intermediate_orders

    # Extract product name and quantity from parameters
    product_name = parameters.get("product_name", "").lower()  # Convert to lowercase to handle case sensitivity
    quantity = parameters.get("quantity", 1)  # Default to 1 if no quantity is specified

    # Ensure the product is in the user's ongoing order
    if user_id not in intermediate_orders or product_name not in intermediate_orders[user_id]:
        return {
            "fulfillmentText": f"The product '{product_name}' is not in your current order. Please check your order and try again."
        }

    # Check if quantity to remove is valid
    quantity = int(quantity)  # Ensure quantity is an integer
    current_quantity = intermediate_orders[user_id].get(product_name, 0)

    if quantity > current_quantity:
        return {
            "fulfillmentText": f"You cannot remove {quantity} of '{product_name}' because your current order only has {current_quantity}."
        }

    # Remove the product from the order or adjust the quantity
    if quantity == current_quantity:
        del intermediate_orders[user_id][product_name]  # Completely remove the product
    else:
        intermediate_orders[user_id][product_name] -= quantity  # Decrease the quantity

    # Prepare the updated order summary
    order_summary = "\n".join(
        [f"{item}: {qty}" for item, qty in intermediate_orders[user_id].items()]
    )

    return {
        "fulfillmentText": f"Your updated order:\n{order_summary}\nWould you like to add or modify items?"
    }


def handle_confirm_order(user_id):
    global intermediate_orders

    if user_id not in intermediate_orders or not intermediate_orders[user_id]:
        return {"fulfillmentText": "Your order is empty. Please add items before confirming."}

    order_details = intermediate_orders[user_id]
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Convert the order details into a comma-separated string of product names and quantities
        product_names = ", ".join(order_details.keys())
        quantities = ", ".join(map(str, order_details.values()))

        # Calculate order total using the calculate_order_total function
        order_total = calculate_order_total(order_details)

        # Insert the order into the database
        query = """
            INSERT INTO orders (product_names, quantity, order_status, order_total) 
            VALUES (%s, %s, %s, %s)
        """
        data = (product_names, quantities, "Confirmed", order_total)
        cursor.execute(query, data)
        connection.commit()

        # Get the last inserted order_id (assuming it's auto-incremented)
        order_id = cursor.lastrowid

        # Clear the user's intermediate order after confirmation
        del intermediate_orders[user_id]

        # Return the order confirmation with the order ID
        return {
            "fulfillmentText": f"Your order has been placed successfully! Your order ID is {order_id}. The total amount is ₹{order_total}. Thank you!!!"
        }
    except Exception as e:
        return {"fulfillmentText": f"An error occurred: {str(e)}"}
    finally:
        cursor.close()
        connection.close()


async def handle_track_order(parameters, user_id):
    # Extract the Order_ID from the parameters
    order_id = parameters.get("Order_ID", "")

    if not order_id:
        return {
            "fulfillmentText": "Please provide a valid Order ID to track your order."
        }

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Query the database for the order details
        query = "SELECT order_status, order_total FROM orders WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        order = cursor.fetchone()

        if order:
            order_status = order["order_status"]
            order_total = order["order_total"]
            return {
                "fulfillmentText": f"Order ID {order_id} Status: {order_status}. Total Amount: ₹{order_total}."
            }
        else:
            return {
                "fulfillmentText": f"No order found with Order ID {order_id}. Please check and try again."
            }
    except Exception as e:
        return {
            "fulfillmentText": f"An error occurred while tracking your order: {str(e)}"
        }
    finally:
        cursor.close()
        connection.close()
