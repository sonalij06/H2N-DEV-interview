# import xml.etree.ElementTree as ET
# import json
# import logging
# from datetime import datetime
# import os

# # Setting up logging
# log_file = "./logs/process.log"
# logging.basicConfig(filename=log_file, level=logging.INFO)

# def log_error(message):
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     logging.error(f"{timestamp}: {message}")

# def log_info(message):
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     logging.info(f"{timestamp}: {message}")

# # Function to clean XML content and remove BOM if present
# def clean_xml(xml_content):
#     return xml_content.encode('utf-8').decode('utf-8-sig')

# # Function to parse XML and convert it to JSON
# def parse_xml_to_json(file_path):
#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             xml_content = file.read()
        
#         # Clean the XML content
#         xml_content = clean_xml(xml_content)
        
#         # Parse the XML content
#         root = ET.fromstring(xml_content)
        
#         # Prepare to capture all orders
#         all_orders_data = []

#         # Check if the root is <Orders> or <Order>
#         if root.tag == 'Orders':
#             # Loop through each Order
#             for order in root.findall('Order'):
#                 order_data = extract_order_data(order)
#                 all_orders_data.append(order_data)
        
#         elif root.tag == 'Order':
#             # Process single order
#             order_data = extract_order_data(root)
#             all_orders_data.append(order_data)
        
#         else:
#             log_error(f"{file_path} - Unexpected root element: {root.tag}.")
#             return None

#         # Convert all orders to JSON
#         json_data = json.dumps(all_orders_data, indent=4)

#         # Log success
#         log_info(f"Processed {file_path} successfully.")
#         return json_data

#     except ET.ParseError as e:
#         log_error(f"Parsing error in {file_path} - {e}")
#         return None
#     except Exception as e:
#         log_error(f"General error in {file_path} - {e}")
#         return None

# def extract_order_data(order):
#     order_data = {
#         "OrderID": order.findtext('OrderID'),
#         "OrderDate": order.findtext('OrderDate'),
#         "TotalAmount": order.findtext('TotalAmount'),
#         "Customer": {}
#     }

#     # Check for customer information if available
#     customer = order.find('Customer')
#     if customer is not None:
#         order_data["Customer"] = {
#             "CustomerID": customer.findtext('CustomerID'),
#             "Name": customer.findtext('Name')
#         }

#     # Extract products if they exist
#     order_data["Products"] = []
#     products = order.find('Products')
#     if products is not None:
#         for product in products.findall('Product'):
#             product_data = {
#                 "ProductID": product.findtext('ProductID'),
#                 "Name": product.findtext('Name'),
#                 "Quantity": product.findtext('Quantity'),
#                 "Price": product.findtext('Price')
#             }
#             order_data["Products"].append(product_data)

#     # Log missing fields
#     missing_fields = []
#     if not order_data["OrderID"]:
#         missing_fields.append("<OrderID>")
#     if not order_data["OrderDate"]:
#         missing_fields.append("<OrderDate>")
#     if not order_data["TotalAmount"]:
#         missing_fields.append("<TotalAmount>")
#     if not order_data["Customer"].get("CustomerID"):
#         missing_fields.append("<CustomerID>")
#     if not order_data["Customer"].get("Name"):
#         missing_fields.append("<Customer Name>")
    
#     if missing_fields:
#         log_error(f"Missing fields in order {order_data['OrderID']}: {', '.join(missing_fields)}")

#     return order_data

# # Function to process multiple XML files
# def process_xml_files(directory):
#     output_directory = './json-output/'
#     os.makedirs(output_directory, exist_ok=True)
#     for filename in os.listdir(directory):
#         if filename.endswith(".xml"):
#             file_path = os.path.join(directory, filename)
#             json_output = parse_xml_to_json(file_path)
#             if json_output:
#                 json_file_path = os.path.join(output_directory, filename.replace('.xml', '.json'))
#                 with open(json_file_path, 'w', encoding='utf-8') as json_file:
#                     json_file.write(json_output)
#                 print(f"Processed {filename}:\n{json_output}\n")
#             else:
#                 print(f"Skipped {filename} due to errors. See log for details.\n")

# # Example usage
# if __name__ == "__main__":
#     # Make sure the logs directory exists
#     os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
#     process_xml_files('./xml-files-main/')



import xml.etree.ElementTree as ET
import json
import logging
from datetime import datetime
import os
import sqlite3
import time

# Setting up logging
log_file = "./logs/process.log"
logging.basicConfig(filename=log_file, level=logging.INFO)

def log_error(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.error(f"{timestamp}: {message}")

def log_info(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"{timestamp}: {message}")

# Function to clean XML content and remove BOM if present
def clean_xml(xml_content):
    return xml_content.encode('utf-8').decode('utf-8-sig')

# Function to set up SQLite database and tables
def setup_database():
    conn = sqlite3.connect('data_processing.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            xml_content TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            json_content TEXT
        )
    ''')
    conn.commit()
    return conn

# Function to insert raw XML data into the database
def insert_raw_data(conn, filename, xml_content):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO raw_data (filename, xml_content) VALUES (?, ?)", (filename, xml_content))
    conn.commit()

# Function to insert processed JSON data into the database
def insert_processed_data(conn, filename, json_content):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO processed_data (filename, json_content) VALUES (?, ?)", (filename, json_content))
    conn.commit()

# Function to extract order data from XML element
def extract_order_data(order):
    order_data = {
        "OrderID": order.findtext('OrderID'),
        "OrderDate": order.findtext('OrderDate'),
        "TotalAmount": order.findtext('TotalAmount'),
        "Customer": {}
    }

    # Check for customer information if available
    customer = order.find('Customer')
    if customer is not None:
        order_data["Customer"] = {
            "CustomerID": customer.findtext('CustomerID'),
            "Name": customer.findtext('Name')
        }

    # Extract products if they exist
    order_data["Products"] = []
    products = order.find('Products')
    if products is not None:
        for product in products.findall('Product'):
            product_data = {
                "ProductID": product.findtext('ProductID'),
                "Name": product.findtext('Name'),
                "Quantity": product.findtext('Quantity'),
                "Price": product.findtext('Price')
            }
            order_data["Products"].append(product_data)

    # Log missing fields
    missing_fields = []
    if not order_data["OrderID"]:
        missing_fields.append("<OrderID>")
    if not order_data["OrderDate"]:
        missing_fields.append("<OrderDate>")
    if not order_data["TotalAmount"]:
        missing_fields.append("<TotalAmount>")
    if not order_data["Customer"].get("CustomerID"):
        missing_fields.append("<CustomerID>")
    if not order_data["Customer"].get("Name"):
        missing_fields.append("<Customer Name>")
    
    if missing_fields:
        log_error(f"Missing fields in order {order_data['OrderID']}: {', '.join(missing_fields)}")

    return order_data

# Function to parse XML and convert it to JSON with retry mechanism
def parse_xml_to_json(file_path, conn, attempt=1):
    if attempt > 3:
        log_error(f"Max attempts reached for {file_path}. Skipping file.")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()
        
        # Clean the XML content
        xml_content = clean_xml(xml_content)
        
        # Insert raw data into the database
        insert_raw_data(conn, os.path.basename(file_path), xml_content)
        
        # Parse the XML content
        root = ET.fromstring(xml_content)
        
        # Prepare to capture all orders
        all_orders_data = []

        # Check if the root is <Orders> or <Order>
        if root.tag == 'Orders':
            # Loop through each Order
            for order in root.findall('Order'):
                order_data = extract_order_data(order)
                all_orders_data.append(order_data)
        
        elif root.tag == 'Order':
            # Process single order
            order_data = extract_order_data(root)
            all_orders_data.append(order_data)
        
        else:
            log_error(f"{file_path} - Unexpected root element: {root.tag}.")
            return None

        # Convert all orders to JSON
        json_data = json.dumps(all_orders_data, indent=4)

        # Insert processed data into the database
        insert_processed_data(conn, os.path.basename(file_path), json_data)

        # Log success
        log_info(f"Processed {file_path} successfully.")
        return json_data

    except ET.ParseError as e:
        log_error(f"Parsing error in {file_path} - {e}. Retrying...")
        time.sleep(2)  # Wait before retrying
        return parse_xml_to_json(file_path, conn, attempt + 1)  # Retry the parsing
    except Exception as e:
        log_error(f"General error in {file_path} - {e}")
        return None

# Function to process multiple XML files
def process_xml_files(directory):
    output_directory = './json-output/'
    os.makedirs(output_directory, exist_ok=True)  # Create output directory if it doesn't exist

    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            file_path = os.path.join(directory, filename)
            json_output = parse_xml_to_json(file_path, db_conn)
            if json_output:
                # Define the output file path with .json extension
                json_file_path = os.path.join(output_directory, filename.replace('.xml', '.json'))
                with open(json_file_path, 'w', encoding='utf-8') as json_file:
                    json_file.write(json_output)
                print(f"Processed {filename} and saved JSON to {json_file_path}\n")
            else:
                print(f"Skipped {filename} due to errors. See log for details.\n")

# Example usage
if __name__ == "__main__":
    # Make sure the logs directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Set up the SQLite database
    db_conn = setup_database()

    process_xml_files('./xml-files/')

    # Close the database connection
    db_conn.close()
