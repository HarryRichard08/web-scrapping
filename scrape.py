from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2

# demo
#smart bots pipeline check

# Define a function to scrape the website and return data as a variable
def scrape_website():
    # Make a request to the website
    r = requests.get("https://books.toscrape.com")

    # Create a BeautifulSoup object and specify the parser
    soup = BeautifulSoup(r.text, 'html.parser')

    # Find all the books on the page
    books = soup.find_all('article', class_='product_pod')

    # Initialize an empty list for storing book details
    book_details = []

    # Iterate through each book and get details
    for book in books:
        title = book.h3.a.get('title')
        price = book.find('p', class_='price_color').text
        availability = book.find('p', class_='instock availability').text.strip()
        book_details.append([title, price, availability])

    return book_details

# Define a function to clean the data
def clean_data(book_details):
    # Convert the book details to a DataFrame
    data = pd.DataFrame(book_details, columns=['Title', 'Price', 'Availability'])

    # Perform data cleaning here, e.g., removing £ sign from price
    data['Price'] = data['Price'].str.replace('£', '')

    # Remove any non-numeric characters from the "Price" column
    data['Price'] = data['Price'].str.replace('[^\d.]', '', regex=True)

    # Encode and decode Price data to handle encoding issues
    data['Price'] = data['Price'].str.encode('utf-8').str.decode('utf-8')

    return data

# Define a function to insert cleaned data into PostgreSQL
def insert_data_into_postgres(data):
    # Define your PostgreSQL connection parameters
    DB_HOST = "db-postgresql-sfo3-smartbot-1db-do-user-8157534-0.b.db.ondigitalocean.com"
    DB_PORT = "25060"
    DB_NAME = "alpha"
    DB_USER = "doadmin"
    DB_PASSWORD = "mq2i4pwpvlen6mho"
    DB_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()

    # Insert data into the PostgreSQL database
    for _, row in data.iterrows():
        cur.execute(
            "INSERT INTO book_details (title, price, availability) VALUES (%s, %s, %s)",
            (row['Title'], row['Price'], row['Availability'])
        )

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 8, 4),
    'retries': 1,
}

# Create the DAG
dag = DAG(
    'scraper',
    default_args=default_args,
    description='A simple book scraper',
    schedule_interval='@once',
)

# Create tasks using PythonOperator
scrape_website_task = PythonOperator(
    task_id='scrape_website',
    python_callable=scrape_website,
    dag=dag,
)

clean_data_task = PythonOperator(
    task_id='clean_data',
    python_callable=clean_data,
    op_args=[scrape_website_task.output],  # Pass the output of the previous task
    dag=dag,
)

# Create a task to insert data into PostgreSQL
insert_data_task = PythonOperator(
    task_id='insert_data_into_postgres',
    python_callable=insert_data_into_postgres,
    op_args=[clean_data_task.output],  # Pass the output of the previous task
    dag=dag,
)

# Define task dependencies
scrape_website_task >> clean_data_task >> insert_data_task
