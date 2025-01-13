**OrderBot - Chatbot for Placing and Tracking Orders**

**Overview**
OrderBot is a chatbot built using Dialogflow, FastAPI, and MySQL. The chatbot is designed to help users place and track orders for a shop. It can answer product inquiries, place orders, and provide real-time order status updates. The project also includes a simple web interface to interact with the chatbot, integrated with the Dialogflow agent.


**Features**
- **Order Placement**: Users can place new orders by interacting with the chatbot. The chatbot will collect product details and the desired quantity, then confirm the order.
- **Order Status Tracking**: The chatbot allows users to track the status of their orders, displaying the current status (Confirmed, Shipped, Delivered, Cancelled).
- **Product Query**: Users can ask for product details, availability, and prices. The chatbot will provide the requested information from the product database.
- **Backend Integration**: FastAPI acts as the backend, managing communication between the chatbot (Dialogflow) and the MySQL database.
- **Error Handling**: The system ensures smooth operation, providing appropriate error messages and guidance if something goes wrong during the interaction.

**Technologies Used**
Dialogflow: A natural language processing tool used to create conversational agents (chatbots).
FastAPI: A Python web framework used for building the RESTful API and serving the web interface.
MySQL: A relational database management system used for storing product and order data.
Jinja2: A templating engine used for rendering HTML pages in FastAPI.

**Detailed Explanation**
This project is designed to build an interactive chatbot that allows users to place and track orders for a shop. The frontend is hosted on a webpage using FastAPI, which serves HTML templates rendered with Jinja2. These templates are dynamically populated with information about products and order statuses. The core conversational logic is managed by Dialogflow, where the chatbot understands user queries related to product availability, placing orders, and tracking orders. Dialogflow interacts with FastAPI through webhooks, where FastAPI exposes endpoints to handle requests from the chatbot. The FastAPI app handles the backend logic, processes requests from Dialogflow, interacts with the MySQL database, and sends responses back to Dialogflow to guide the conversation.

On the backend, the project utilizes a MySQL database to store and manage product and order data. The database consists of two main tables: products to store product details like name, price, and stock, and orders to store customer orders along with their status and totals. FastAPI routes are implemented for querying products, placing orders, and tracking the status of orders. These routes interact with the MySQL database to retrieve product data and update order information as users interact with the chatbot. Ngrok is used during development to expose the FastAPI server to the internet for testing purposes, allowing Dialogflow to make requests to the local server. The entire project brings together FastAPI, MySQL, Dialogflow, and Jinja2 templating to create a seamless and interactive order management experience.



**Database Schema**
Orders Table
The `orders` table stores information about each order placed.

| Column        | Type               | Description                                  |
|---------------|--------------------|----------------------------------------------|
| order_id      | int (PK, AI)        | Unique identifier for the order.             |
| product_names | varchar(255)        | List of product names in the order.          |
| quantity      | varchar(255)        | List of quantities for each product.         |
| order_status  | enum               | Status of the order (`Confirmed`, `Shipped`, `Delivered`, `Cancelled`). |
| order_total   | decimal(10, 2)      | Total cost of the order.                     |

Products Table
The `products` table stores details about products available in the shop.

| Column        | Type               | Description                                  |
|---------------|--------------------|----------------------------------------------|
| Product_ID    | int (PK, AI)        | Unique identifier for the product.           |
| Product_Name  | varchar(255)        | Name of the product.                         |
| Stock         | int                | Quantity of the product available in stock.  |
| Product_Price | int                | Price of the product.                        |




**Project Setup Guide**

#### 1. **Dialogflow Setup and Agent Creation**
- Sign in to Dialogflow and create a new agent for the project. Provide a suitable name and set up the language and Google Cloud project.
- Define key intents for the chatbot, such as product inquiries, order status, and placing orders.
- In the Fulfillment settings, enable webhook calls and configure the webhook URL to point to your FastAPI backend.

#### 2. **Setting Up FastAPI for Webhook Integration**
- Install the necessary dependencies, including FastAPI, and create an endpoint to handle webhook requests from Dialogflow.
- This webhook processes user inputs, identifies the intent, and interacts with the database to retrieve or update information as required.

#### 3. **Database Configuration**
- Create a MySQL database to store product details and order records.
- Define two tables:
  - `products`: Stores product information, including name, stock, and price.
  - `orders`: Stores order details, including product names, quantities, status, and total cost.
- Populate the `products` table with initial data for testing purposes.

#### 4. **Building the Website**
- Use an HTML template for creating a simple web interface to interact with the chatbot.
- Integrate the Dialogflow chatbot into the webpage, enabling users to interact with the chatbot directly from their browser.
- Render the HTML using FastAPI’s templating system.

#### 5. **Testing and Running the Application**
- Start the FastAPI server to host the webhook and the webpage.
- Open the webpage locally to interact with the chatbot and test its functionalities, such as placing and tracking orders.

#### 6. **Optional: Exposing the Application with Ngrok**
- Install and use Ngrok to expose your local FastAPI server to the internet for remote testing.
- Update the webhook URL in Dialogflow with the public URL provided by Ngrok.
