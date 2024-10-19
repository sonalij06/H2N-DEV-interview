import unittest
from unittest.mock import patch, mock_open, MagicMock
import xml.etree.ElementTree as ET
import json
import logging
import os
import sqlite3
from scripts.parsing_xml import (
    log_error,
    log_info,
    clean_xml,
    setup_database,
    insert_raw_data,
    insert_processed_data,
    extract_order_data,
    parse_xml_to_json
)

class TestXMLProcessing(unittest.TestCase):
    
    @patch('logging.error')
    def test_log_error(self, mock_log_error):
        log_error("Test error message")
        self.assertTrue(mock_log_error.called)
        
    @patch('logging.info')
    def test_log_info(self, mock_log_info):
        log_info("Test info message")
        self.assertTrue(mock_log_info.called)

    def test_clean_xml(self):
        test_input = '\ufeff<root></root>'
        expected_output = '<root></root>'
        self.assertEqual(clean_xml(test_input), expected_output)

    def test_setup_database(self):
        conn = setup_database()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        self.assertIn(('raw_data',), tables)
        self.assertIn(('processed_data',), tables)
        conn.close()
        
    # def test_insert_raw_data(self):
    #     conn = sqlite3.connect(':memory:')  # Use an in-memory database
    #     setup_database()
    #     insert_raw_data(conn, "test.xml", "<data></data>")
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT * FROM raw_data")
    #     rows = cursor.fetchall()
    #     self.assertEqual(len(rows), 1)
    #     self.assertEqual(rows[0][1], "test.xml")
    #     conn.close()

    # def test_insert_processed_data(self):
    #     conn = sqlite3.connect(':memory:')  # Use an in-memory database
    #     setup_database()
    #     insert_processed_data(conn, "output.json", '{"key": "value"}')
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT * FROM processed_data")
    #     rows = cursor.fetchall()
    #     self.assertEqual(len(rows), 1)
    #     self.assertEqual(rows[0][1], "output.json")
    #     conn.close()

    def test_extract_order_data(self):
        xml_data = '''
        <Order>
            <OrderID>123</OrderID>
            <OrderDate>2024-10-15T10:30:00</OrderDate>
            <TotalAmount>100.00</TotalAmount>
            <Customer>
                <CustomerID>456</CustomerID>
                <Name>Test Customer</Name>
            </Customer>
            <Products>
                <Product>
                    <ProductID>789</ProductID>
                    <Name>Test Product</Name>
                    <Quantity>1</Quantity>
                    <Price>100.00</Price>
                </Product>
            </Products>
        </Order>
        '''
        root = ET.fromstring(xml_data)
        order_data = extract_order_data(root)
        self.assertEqual(order_data['OrderID'], '123')
        self.assertEqual(order_data['Customer']['Name'], 'Test Customer')

    @patch('builtins.open', new_callable=mock_open, read_data='''<Order>
        <OrderID>123</OrderID>
        <OrderDate>2024-10-15T10:30:00</OrderDate>
        <TotalAmount>100.00</TotalAmount>
        <Customer>
            <CustomerID>456</CustomerID>
            <Name>Test Customer</Name>
        </Customer>
        <Products>
            <Product>
                <ProductID>789</ProductID>
                <Name>Test Product</Name>
                <Quantity>1</Quantity>
                <Price>100.00</Price>
            </Product>
        </Products>
    </Order>''')
    @patch('scripts.parsing_xml.insert_raw_data')  # Adjust the import as necessary
    @patch('scripts.parsing_xml.insert_processed_data')
    def test_parse_xml_to_json(self, mock_insert_processed_data, mock_insert_raw_data, mock_open):
        conn = sqlite3.connect(':memory:')  # Use an in-memory database
        setup_database()
        
        json_output = parse_xml_to_json('test.xml', conn)
        expected_json = json.dumps([{
            "OrderID": "123",
            "OrderDate": "2024-10-15T10:30:00",
            "TotalAmount": "100.00",
            "Customer": {
                "CustomerID": "456",
                "Name": "Test Customer"
            },
            "Products": [{
                "ProductID": "789",
                "Name": "Test Product",
                "Quantity": "1",
                "Price": "100.00"
            }]
        }], indent=4)

        self.assertEqual(json_output, expected_json)
        conn.close()

    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.parsing_xml.log_error')
    def test_parse_xml_to_json_invalid_xml(self, mock_log_error, mock_open):
        mock_open.return_value.read.return_value = "<InvalidXML"
        conn = sqlite3.connect(':memory:')
        setup_database()
        json_output = parse_xml_to_json('invalid.xml', conn)
        self.assertIsNone(json_output)
        self.assertTrue(mock_log_error.called)

if __name__ == '__main__':
    unittest.main()
