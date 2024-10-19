# XML to JSON Converter

## Overview
This project provides a utility to convert XML files containing order data into JSON format. It also logs processing steps, handles errors with a retry mechanism, and stores raw and processed data in an SQLite database.

## Use Cases
1. **Convert XML to JSON**: Automate the conversion of XML files containing order data to JSON format for easier consumption by other systems or services.
  
2. **Error Handling**: Automatically retry parsing of XML files up to three times if a parsing error occurs, ensuring robustness against transient errors.

3. **Data Logging**: Maintain a detailed log of processing steps, including errors encountered, for audit and debugging purposes.

4. **Data Storage**: Store raw XML content and processed JSON data in an SQLite database for future reference and analysis.

5. **Batch Processing**: Process multiple XML files from a specified directory, saving the resulting JSON files to a designated output directory.

## Getting Started

### Prerequisites
- Python 3.x
- Required Python packages:
  - `xml.etree.ElementTree` (standard library)
  - `json` (standard library)
  - `sqlite3` (standard library)
  - `logging` (standard library)

### Installation
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd xml-to-json
2. (Optional) Set up a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

## Running the Converter
1. Prepare your XML files and place them in the xml-files/ directory.
2. Run the conversion script:
      ```bash
      python scripts/parsing_xml.py
3. The processed JSON files will be saved in the ```json-output/``` directory, and logs will be created in the ```logs/``` directory.

## Error Handling
If there are any issues with parsing XML files, the script will attempt to retry the parsing up to three times. Details of any errors will be logged in the ```logs/process.log``` file.

## Database
The project uses an SQLite database to store both raw XML content and processed JSON data.
The database file (```data_processing.db```) will be created in the project root directory.
## Unit Testing
Unit tests are implemented using the unittest framework to ensure the correctness of the XML parsing and logging functionality.
To run the tests, execute:
      ```python -m unittest unit-test/test_parsing_xml.py ```
