import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

url = "https://github.com/Ouckah/Summer2025-Internships"

# Fetch the content from the URL
response = requests.get(url).text

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(response, 'lxml')

# Find the div containing the table
div = soup.find('div', class_='Box-sc-g0xbh4-0 ehcSsh')

if div:
    table = div.find('table')

    if table:
        headers = []

        for header in table.find_all('th'):
            header_text = header.text.strip()
            headers.append(header_text)

        rows = table.find_all('tr')[1:]

        seen_companies = set()  # Set to track companies
        rows_data = []

        for row in rows:
            columns = row.find_all('td')
            if len(columns) > 0:
                company = columns[0].text.strip()
                role = columns[1].text.strip() if len(columns) > 1 else 'N/A'
                location = columns[2].text.strip() if len(columns) > 2 else 'N/A'
                application_link = columns[3].find('a')['href'].strip() if len(columns) > 3 and columns[3].find('a') else 'N/A'
                date_posted = columns[4].text.strip() if len(columns) > 4 else 'N/A'

                # Replace '↳' with 'Unknown' for company and handle location
                company = 'Unknown' if company == '↳' else company
                location = location.replace('locations ', '')

                # Check if location contains numbers and set to 'multiple locations' if so
                if re.search(r'\d', location):
                    location = 'multiple locations'

                # Skip duplicates
                if company not in seen_companies:
                    seen_companies.add(company)
                    row_data = {
                        'Company': company,
                        'Role': role,
                        'Location': location,
                        'Application/Link': application_link,
                        'Date Posted': date_posted
                    }
                    rows_data.append(row_data)

        # Create a DataFrame from the rows_data
        df = pd.DataFrame(rows_data)

        # Print the DataFrame
        print(df)

    else:
        print('No table found')
else:
    print('No Div found')
