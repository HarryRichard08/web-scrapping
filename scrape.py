import requests
#from bs4 import BeautifulSoup

#working demo 
#working demo
# URL of the webpage to scrape
url = "https://www.example-news-site.com"

# Send an HTTP GET request to the URL
response = requests.get(url)

# Parse the HTML content of the page using Beautiful Soup
soup = BeautifulSoup(response.content, "html.parser")

# Find all the article title elements on the page
article_titles = soup.find_all("h2", class_="article-title")

# Loop through the article title elements and print the titles
for title_element in article_titles:
    title_text = title_element.get_text()
    print("Article Title:", title_text)
# jenkins demo
