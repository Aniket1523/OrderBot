# Imports
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from router import router
from mysql.connector import pooling

# Set up FastAPI
app = FastAPI()

# Include the router that contains the webhook endpoint
app.include_router(router)

# Initialize Jinja2 Templates
templates = Jinja2Templates(directory="static")

# Database connection settings
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "********",
    "database": "********"
}
connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **db_config)

# Serve static files (Product Images)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Helper function to fetch products from the database
def fetch_products():
    # Establish connection to the database
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)

    # Query to fetch product names and prices
    query = "SELECT Product_Name, Product_Price FROM products"
    cursor.execute(query)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return products


# Route to serve the index.html
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    products = fetch_products()

    # Render the template with products data
    return templates.TemplateResponse("index.html", {"request": request, "products": products})
