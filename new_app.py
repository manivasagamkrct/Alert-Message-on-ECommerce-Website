import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration  "C:\Users\tebi\Downloads"
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'mohan357951@gmail.com'  
EMAIL_PASSWORD = 'bekp nogv ackc acjl'  


# Function to validate email
def is_valid_email(email):
    import re
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Function to scrape product details
def scrape_product(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract product title
            title = soup.find('span', {'id': 'productTitle'}).get_text(strip=True) if soup.find('span', {'id': 'productTitle'}) else "Title not found"

            # Extract product price
            price_whole = soup.find('span', {'class': 'a-price-whole'})
            price_fraction = soup.find('span', {'class': 'a-price-fraction'})
            if price_whole and price_fraction:
                price = f"{price_whole.get_text(strip=True)}.{price_fraction.get_text(strip=True)}"
            else:
                price = "Price not found"
            
            return {'Title': title, 'Price': price, 'URL': url}
        else:
            return {'Title': "Failed to retrieve", 'Price': "Failed to retrieve", 'URL': url}
    except Exception as e:
        return {'Title': "Error", 'Price': str(e), 'URL': url}

# Function to send email
def send_email(subject, body, recipient_email):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        return str(e)

# Streamlit UI
st.title("🛠️ Product Price Scraper") 

# User input for URLs and recipient email
url_input = st.text_area("Enter Amazon Product URLs (one per line):", "")
recipient_email = st.text_input("Enter Recipient Email:", "")

if st.button("Scrape and Send Email"):
    if url_input and recipient_email:
        # Validate the email format
        if not is_valid_email(recipient_email):
            st.warning("Please enter a valid email address.")
        else:
            urls = url_input.splitlines()  # Split input into a list of URLs
            all_products = []  # Store product details
            email_body = "Product Price Report:\n\n"

            for url in urls:
                if url.strip():  # Ensure the URL is not empty
                    product_data = scrape_product(url.strip())
                    all_products.append(product_data)

                    # Append each product's details to the email body separately
                    email_body += (f"Title: {product_data['Title']}\n"
                                   f"Price: {product_data['Price']}\n"
                                   f"URL: {product_data['URL']}\n"
                                   f"{'-' * 50}\n")  # Separator line between products

                    # Display each product result in Streamlit
                    st.write(f"### Product Details:")
                    st.write(f"**Title:** {product_data['Title']}")
                    st.write(f"**Price:** {product_data['Price']}")

                    st.write(f"[View Product]({product_data['URL']})")
                    st.write(f"{'-' * 50}")  # Separator for UI clarity

            # Save data to CSV
            csv_file = "price_history.csv"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for product in all_products:
                    writer.writerow([timestamp, product['Title'], product['Price'], product['URL']])

            # Send email
            email_status = send_email("Product Price Report", email_body, recipient_email)
            if email_status == True:
                st.success("Product details emailed successfully!")
            else:
                st.error(f"Failed to send email: {email_status}")
    else:
        st.warning("Please enter valid Amazon product URLs and a recipient email.")
