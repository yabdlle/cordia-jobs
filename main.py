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
    job_keywords = ['Software Engineer', 'Software Developer', 'Software Engineering']
    return get_Data(keywords=job_keywords)

def get_FullStack():
    job_keywords = ['Full Stack', 'Full-Stack', 'Front End', 'Back end', 'Backend', 'Frontend', 'Front-end', 'Back-end']
    return get_Data(keywords=job_keywords)

def get_It():
    job_keywords = ['Cloud', 'DevOps', 'IT', 'Cyber', 'Risk', 'Support', 'Administrator', 'Cybersecurity', 'Analyst', 'Business' 'Information Technology']
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
async def fetch_recent_jobs(ctx, role_keyword: str = None, num_jobs: int = 5):
    now = datetime.now(pytz.utc)
    current_year = 2024
    recent_jobs = []

    ROLE_MAPPINGS = {
        'swe': ['Software Engineer'],
        'sde': ['Software Developer'],
        'fullstack': ['Full Stack Developer'],
        'frontend': ['Frontend Developer'],
        'backend': ['Backend Developer'],
        'it': ['IT Specialist'],
        'sysadmin': ['System Administrator'],
        'ML': ['Machine Learning Engineer'],
        'AI': ['AI Engineer'],
        'Embed': ['Embedded Engineer']
    }
    
    if role_keyword:
        role_keyword = role_keyword.lower()
        full_role_names = ROLE_MAPPINGS.get(role_keyword, [role_keyword])
    else:
        full_role_names = []

    df = get_Data(keywords=full_role_names)

    if df is None or df.empty:
        await ctx.send("No data available.")
        return

    for index, row in df.iterrows():
        date_posted_str = row['Date Posted']
        try:
            date_posted_str_with_year = f"{current_year} {date_posted_str}"
            date_posted = datetime.strptime(date_posted_str_with_year, '%Y %b %d').replace(tzinfo=pytz.utc)
            time_difference = (now - date_posted).total_seconds()

            if time_difference <= 172800:
                recent_jobs.append(row)
        except ValueError:
            continue

    job_count_message = f"Number of jobs within the last 48 hours for roles {', '.join(full_role_names)}: {len(recent_jobs)}"
    await ctx.send(job_count_message)

    if not recent_jobs:
        await ctx.send(f"No recent jobs found for roles: {', '.join(full_role_names)}.")
        return

    response = ""
    for row in recent_jobs[:num_jobs]:
        response += format_job_data(row)

    await text_length(ctx, response)




@client.command(name='commands')
async def fetch_commands(ctx):
    commands_list = (
        "**Available Commands:**\n\n"
        "`?company [company_name] [role]` - Get job postings for the specified company and role (if exists).\n"
        "`?recent [role] [num_jobs]` - Get a list of the most recent jobs for a specified role (default: 5).\n"
        "`?jobs [num_jobs]` - Get a list of the most recent jobs (default: 5).\n"
        "`?swe [num_jobs]` - Get a list of the most recent Software Engineering Internships (default: 5).\n"
        "`?fullstack [num_jobs]` - Get a list of the most recent Full Stack, Backend, and Front End Internships (default: 5).\n"
        "`?it [num_jobs]` - Get a list of the most recent IT-related Internships (default: 5).\n"
        "`?random [num_jobs]` - Get a random list of internships posted (default: 5).\n"
        "`?lo [num_jobs]` - Retrieve a list of job postings for a specified location (default: 5).\n"
        "`?remote [num_jobs]` - Fetch a list of remote job opportunities (default: 5).\n"
        "`?src` - Get the source of internship data.\n"
        "`?git` - Get the Github code of the bot.\n"
    )
    await ctx.send(commands_list)


def search_company_by_index(companies, role_keyword=None):
    ROLE_MAPPINGS = {
        'swe': 'Software Engineer',
        'sde': 'Software Developer',
        'fullstack': 'Full Stack Developer',
        'frontend': 'Frontend Developer',
        'backend': 'Backend Developer',
        'it': 'IT Specialist',
        'sysadmin': 'System Administrator',
        'ML': 'Machine Learning Engineer',
        'AI': 'AI Engineer',
        'Embed': 'Embedded Engineer'
    }

  
    if role_keyword:
        role_keyword = role_keyword.lower()
        full_role_name = ROLE_MAPPINGS.get(role_keyword, role_keyword)
    else:
        full_role_name = None

  
    company_list = [company.strip() for company in companies.split(',')]
    
    print(f"Company list: {company_list}")  
    print(f"Role keyword: {full_role_name}")  

    #
    df = get_Data(keywords=[full_role_name] if full_role_name else [], filter_keywords=company_list)
    

    if df is not None and not df.empty:
        print(f"Fetched DataFrame:\n{df.head()}")  
    else:
        print("No data fetched or DataFrame is empty.")

    if df is None or df.empty:
        return "No job postings found. Please check the company names and roles."

  
    response = ""
    for _, row in df.iterrows():
        role = row['Role'].lower()
        if full_role_name and full_role_name.lower() not in role:
            continue
        response += format_job_data(row)

    if not response:
        return f"No job postings found for companies '{', '.join(company_list)}' with the role keyword '{role_keyword}'."
    
    return response

@client.command(name='company')
async def search_company(ctx, companies: str, *, role_keyword: str = None):
    result = search_company_by_index(companies, role_keyword)
    await ctx.send(result)




@client.command(name='random')
async def random_job(ctx, num_jobs: int = 5):
    df = get_Data([])  
    if df is None or df.empty:
        await ctx.send("No jobs available.")
        return


    now = datetime.now(pytz.utc)


    start_of_week = now - timedelta(days=now.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    recent_jobs = []
    for index, row in df.iterrows():
        date_posted_str = row['Date Posted']
        try:
         
            date_posted = datetime.strptime(f"{datetime.now().year} {date_posted_str}", '%Y %b %d').replace(tzinfo=pytz.utc)

            # Check if the date is within the current week
            if start_of_week <= date_posted <= end_of_week:
                recent_jobs.append(row)
        except ValueError:
            continue

    if not recent_jobs:
        await ctx.send("No job postings found from the current week.")
        return

    # Select a random sample of jobs
    num_jobs = min(max(1, num_jobs), len(recent_jobs))
    random_rows = pd.DataFrame(recent_jobs).sample(n=num_jobs)

    # Format and send the response
    response = ""
    for _, row in random_rows.iterrows():
        response += format_job_data(row)

    await text_length(ctx, response)
    
@client.command(name='lo')
async def search_location(ctx, *, args: str):
    args_split = args.split()
    
    if not args_split:
        await ctx.send("Please provide a location.")
        return

    default_num_lo = 5

    try:
        num_lo = int(args_split[-1])
        location = ' '.join(args_split[:-1])
    except ValueError:
        location = ' '.join(args_split)
        num_lo = default_num_lo

    df = get_Data([])

    if df is None or df.empty:
        await ctx.send("No job data available.")
        return

    location_keyword = location.lower()
    
    if not all(col in df.columns for col in ['Company', 'Role', 'Location', 'Application/Link', 'Date Posted']):
        await ctx.send("Data format is incorrect.")
        return

    all_locations = df['Location'].str.lower().unique()
    matched_locations = [loc for loc in all_locations if location_keyword in loc]

    if not matched_locations:
        await ctx.send(f"No job postings found for the location '{location}'.")
        return

    filtered_df = df[df['Location'].str.lower().isin(matched_locations)]
    
    num_lo = max(1, num_lo)
    filtered_df = filtered_df.head(num_lo)

    response = ""
    for _, row in filtered_df.iterrows():
        response += format_job_data(row)
    
    await text_length(ctx, response)



@client.command(name='remote')
async def search_remote(ctx, num_jobs: int = 5):
    df = get_Data([])

    if df is None or df.empty:
        await ctx.send("No jobs available.")
        return

    remote_jobs = df[df['Location'].str.contains('remote', case=False, na=False)]

    if remote_jobs.empty:
        await ctx.send("No remote job postings available.")
        return

    num_jobs = max(1, num_jobs)
    remote_jobs = remote_jobs.head(num_jobs)

    response = ""
    for _, row in remote_jobs.iterrows():
        location = row['Location']
        # Format location
        location = re.sub(r'(\w+),(\w+)', r'\1, \2', location)
        location = re.sub(r'(\w+)(Remote)', r'\1 / Remote', location)
        row['Location'] = location
        response += format_job_data(row)

    await text_length(ctx, response)


client.run('TOKEN')
