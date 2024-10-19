import sqlite3
from tabulate import tabulate

def read_database(db_name='data_processing.db'):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        # Query raw_data table
        cursor.execute("SELECT * FROM raw_data")
        raw_data_rows = cursor.fetchall()
        raw_data_headers = [description[0] for description in cursor.description]  # Get column names
        print("Raw Data:")
        print(tabulate(raw_data_rows, headers=raw_data_headers, tablefmt='grid'))

        # Query processed_data table
        cursor.execute("SELECT * FROM processed_data")
        processed_data_rows = cursor.fetchall()
        processed_data_headers = [description[0] for description in cursor.description]  # Get column names
        print("\nProcessed Data:")
        print(tabulate(processed_data_rows, headers=processed_data_headers, tablefmt='grid'))

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    read_database()
