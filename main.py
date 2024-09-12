import discord
import asyncio
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import logging
from datetime import datetime, timedelta
import pytz
from discord.ext import commands


logging.basicConfig(filename='internship_data.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a bot instance with the necessary intents
intents = discord.Intents.default()
intents.message_content = True  
client = commands.Bot(command_prefix='?', intents=intents)
url = "https://github.com/Ouckah/Summer2025-Internships"


def get_Data(keywords, filter_keywords=None):
    if keywords is None:
        keywords = []

    try:
        response = requests.get(url).text
        print(f"Fetched HTML: {response[:500]}")  # Print the first 500 characters of the HTML to debug
        soup = BeautifulSoup(response, 'lxml')
        div = soup.find('div', class_='Box-sc-g0xbh4-0 ehcSsh')

        if div:
            table = div.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip the header
                rows_data = []
                seen_companies_locations = {}

                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) > 0:
                        company = columns[0].text.strip()
                        role = columns[1].text.strip() if len(columns) > 1 else 'N/A'
                        location = columns[2].text.strip() if len(columns) > 2 else 'N/A'
                        link = columns[3].find('a')['href'].strip() if len(columns) > 3 and columns[3].find('a') else 'N/A'
                        date_posted = columns[4].text.strip() if len(columns) > 4 else 'N/A'

                        if company == '↳':
                            continue

                        if location.startswith('↳'):
                            location = location[1:].strip()
                        location = location.replace('locations ', '')
                        if re.search(r'\d', location):
                            location = 'multiple locations'

                        # Avoid duplicates
                        if (company in seen_companies_locations and
                                seen_companies_locations[company] == location):
                            continue

                        seen_companies_locations[company] = location

                        row_data = {
                            'Company': company,
                            'Role': role,
                            'Location': location,
                            'Application/Link': link,
                            'Date Posted': date_posted
                        }
                        rows_data.append(row_data)

                df = pd.DataFrame(rows_data)

                if not df.empty:
                    print(f"Initial DataFrame: {df.head()}")  # Check the first few rows of the DataFrame

                # Filter the DataFrame based on keywords for the role
                if keywords:
                    for keyword in keywords:
                        df = df[df['Role'].str.contains(keyword, case=False, na=False)]
                        print(f"Filtered DataFrame with keyword '{keyword}': {df.head()}")  # Print after filtering

                if filter_keywords:
                    for keyword in filter_keywords:
                        df = df[df['Company'].str.contains(keyword, case=False, na=False)]
                        print(f"Filtered DataFrame with company keyword '{keyword}': {df.head()}")

                return df
            else:
                print('No table found')
        else:
            print('No div with the specified class found')
    except Exception as e:
        print(f'An error occurred: {e}')

    return pd.DataFrame()



def format_job_data(row):
    return (f"**Company:** ***__{row['Company']}__***\n"
            f"**Role:** **{row['Role']}**\n"
            f"**Location:** **{row['Location']}**\n"
            f"**Link:** {row['Application/Link']}\n"
            f"**Date:** {row['Date Posted']}\n\n")

def get_Swe():
    job_keywords = ['Software Engineer', 'Software Developer']
    return get_Data(keywords=job_keywords)

def get_FullStack():
    job_keywords = ['Full Stack', 'Full-Stack', 'Front End', 'Back end', 'Backend', 'Frontend', 'Front-end', 'Back-end']
    return get_Data(keywords=job_keywords)

def get_It():
    job_keywords = ['Cloud', 'DevOps', 'IT', 'Cyber', 'Risk', 'Support', 'Administrator', 'Cybersecurity', 'Analyst']
    return get_Data(keywords=job_keywords)


async def text_length(ctx, response):
    if len(response) > 2000:  # Discord message limit is 2000 characters
        await ctx.send("Data too long to display in one message. Here's a snippet:")
        await ctx.send(response[:2000])
        await ctx.send("... [Data truncated]")
    else:
        await ctx.send(response)

@client.command(name='jobs')
async def fetch_jobs(ctx, num_jobs: int = 5):
    df = get_Data([])
    if df is None or df.empty:
        await ctx.send("No data available.")
        return

    num_jobs = max(1, num_jobs)
    response = ""
    for index, row in df.head(num_jobs).iterrows():
        response += format_job_data(row)

    await text_length(ctx, response)

@client.command(name='getmeajob')
async def get_me_a_job(ctx):
    await ctx.send('Lock in')

@client.command(name='swe')
async def fetch_swe(ctx, num_jobs: int = 5):
    df = get_Swe()
    if df is None or df.empty:
        await ctx.send("No data available.")
        return

    num_jobs = max(1, num_jobs)  # Ensure at least 1 job is requested
    response = ""
    for index, row in df.head(num_jobs).iterrows():
        response += format_job_data(row)

    await text_length(ctx, response)

@client.command(name='fullstack')
async def fetch_full_stack(ctx, num_jobs: int = 5):
    df = get_FullStack()
    if df is None or df.empty:
        await ctx.send("No data available.")
        return

    num_jobs = max(1, num_jobs)  # Ensure at least 1 job is requested
    response = ""
    for index, row in df.head(num_jobs).iterrows():
        response += format_job_data(row)

    await text_length(ctx, response)

@client.command(name='it')
async def fetch_it(ctx, num_jobs: int = 5):
    df = get_It()
    if df is None or df.empty:
        await ctx.send("No data available.")
        return

    num_jobs = max(1, num_jobs)  # Ensure at least 1 job is requested
    response = ""
    for index, row in df.head(num_jobs).iterrows():
        response += format_job_data(row)

    await text_length(ctx, response)

@client.command(name='src')
async def fetch_src(ctx):
    await ctx.send('Check out the source code here: https://github.com/Ouckah/Summer2025-Internships')

@client.command(name='git')
async def fetch_git(ctx):
    await ctx.send('Git Source is here: https://github.com/yabdlle/job-bot/blob/main/main.py')

@client.command(name='recent')
async def fetch_recent_jobs(ctx):
    df = get_Data([])
    if df is None or df.empty:
        await ctx.send("No data available.")
        return

    now = datetime.now(pytz.utc)
    current_year = 2024
    recent_jobs = []

    print(f"Current time (UTC): {now}")

    for index, row in df.iterrows():
        date_posted_str = row['Date Posted']
        print(f"Processing date: {date_posted_str}")
        
        try:
            # Construct date string with the current year
            date_posted_str_with_year = f"{current_year} {date_posted_str}"
            date_posted = datetime.strptime(date_posted_str_with_year, '%Y %b %d').replace(tzinfo=pytz.utc)
            
            print(f"Parsed date (UTC): {date_posted}")
            
            # Calculate time difference in seconds
            time_difference = (now - date_posted).total_seconds()
            print(f"Time difference: {time_difference} seconds")

            if time_difference <= 172800:  # 48 hours
                recent_jobs.append(row)
        except ValueError:
            print(f"Date parsing error: {date_posted_str}")
            continue

    # Print and send the number of jobs within the last 48 hours
    job_count_message = f"Number of jobs within the last 48 hours: {len(recent_jobs)}"
    print(job_count_message)
    await ctx.send(job_count_message)

    if not recent_jobs:
        await ctx.send("No jobs found in the last 48 hours.")
        return

    response = ""
    for row in recent_jobs:  
        response += format_job_data(row)

    await text_length(ctx, response)

@client.command(name='commands')
async def fetch_commands(ctx):
    commands_list = (
        "**Available Commands:**\n\n" 
        "`?company [company_name] [role]` - Get the x company with y role.\n"
        "`?recent` - Get jobs posted in the last 48 hours.\n"
        "`?jobs [num_jobs]` - Get a list of the most recent jobs (default: 5).\n"
        "`?swe [num_jobs]` - Get a list of most recent Software Engineering Internships (default: 5).\n"
        "`?fullstack [num_jobs]` - Get a list of most recent Full Stack, Backend, and Front End Internships (default: 5).\n"
        "`?it [num_jobs]` - Get a list of most recent IT-related Internships (default: 5).\n"
        "`?recent` - Get jobs posted in the last 48 hours.\n"
        "`?src` - Get the source code URL.\n"
        "`?git` - Get the GitHub source code URL.\n"
    )
    await ctx.send(commands_list)

def search_company_by_index(company_name, role_keyword=None):
    ROLE_MAPPINGS = {
        'swe': 'Software Engineer',
        'sde' : 'Software Developer',
        'fullstack': 'Full Stack Developer',
        'frontend': 'Frontend Developer',
        'backend': 'Backend Developer',
        'it': 'IT Specialist',
        'sysadmin': 'System Administrator',
        # Add more mappings as needed
    }

    # Replace role_keyword with the full role name using the ROLE_MAPPINGS dictionary
    if role_keyword:
        role_keyword = role_keyword.lower()
        full_role_name = ROLE_MAPPINGS.get(role_keyword, role_keyword)
    else:
        full_role_name = None

    # Call get_Data with both company name and role keyword filters
    df = get_Data(keywords=[full_role_name] if full_role_name else [], filter_keywords=[company_name])
    
    if df is None or df.empty:
        return "They Aint Drop Yet Bruh. Wait Up"

    # Format and return the results
    response = ""
    for _, row in df.iterrows():
        role = row['Role'].lower()
        if full_role_name and full_role_name.lower() not in role:
            continue
        response += format_job_data(row)

    if not response:
        return f"No job postings found for '{company_name}' with the role keyword '{role_keyword}'."
    
    return response




@client.command(name='company')
async def search_company(ctx, company_name: str, *, role_keyword: str = None):
    result = search_company_by_index(company_name, role_keyword)
    await ctx.send(result)



client.run('TOKEN')
