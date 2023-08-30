from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

#demo 

def scrape_website():
    # Make a request to the website
    r = requests.get("https://books.toscrape.com")

    # Create a BeautifulSoup object and specify the parser
    soup = BeautifulSoup(r.text, 'html.parser')

    # Find all the books on the page
    books = soup.find_all('article', class_='product_pod')

    # Initialize empty list for storing book details
    book_details = []

    # Iterate through each book and get details
    for book in books:
        title = book.h3.a.get('title')
        price = book.find('p', class_='price_color').text
        availability = book.find('p', class_='instock availability').text.strip()
        book_details.append([title, price, availability])

    # Write the book details to a CSV file
    with open('/tmp/book_details.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Price', 'Availability'])
        writer.writerows(book_details)


def clean_data():
    # Load the data from CSV
    data = pd.read_csv('/tmp/book_details.csv')

    # Perform data cleaning here, e.g., removing £ sign from price
    data['Price'] = data['Price'].str.replace('£', '')

    # Save the cleaned data back to CSV
    data.to_csv('/tmp/book_details_clean.csv', index=False)


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 8, 4),
    'retries': 1,
}

dag = DAG(
    'book_scraper',
    default_args=default_args,
    description='A simple book scraper',
    schedule_interval='@daily',
)

scrape_website_task = PythonOperator(
    task_id='scrape_website',
    python_callable=scrape_website,
    dag=dag,
)

clean_data_task = PythonOperator(
    task_id='clean_data',
    python_callable=clean_data,
    dag=dag,
)

# Assume you want to move the clean data to a new location
transfer_data_task = BashOperator(
    task_id='transfer_data',
    bash_command='mv /tmp/book_details_clean.csv ~/store_files_airflow/',
    dag=dag,
)

# Define task dependencies
scrape_website_task >> clean_data_task >> transfer_data_task
