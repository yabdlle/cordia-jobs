Job Data Discord Bot
Welcome to the Job Data Discord Bot! This bot scrapes job postings from a specific URL and provides updates and commands to interact with job data. It is designed to help users find and track internship opportunities.

Features
Fetch Job Data: Retrieve job postings with commands like ?jobs, ?swe, ?fullstack, and ?it.
Recent Jobs: Get a list of jobs posted in the last 48 hours with ?recent.
Periodic Updates: The bot checks for new job postings every minute and posts updates in a specified channel.
Command List: Access a list of available commands with ?commands.
Source Code: Retrieve links to the source code with ?src and ?git.
Setup
Prerequisites
Python 3.8 or later
Discord.py library
Pandas library
Requests library
BeautifulSoup library
Logging library
Installation
Clone the Repository

bash
Copy code
git clone https://github.com/yourusername/job-bot.git
cd job-bot
Install Dependencies

Ensure you have pip installed, then run:

bash
Copy code
pip install -r requirements.txt
Setup Environment Variables

Create a .env file in the project directory and add your Discord bot token:

env
Copy code
DISCORD_TOKEN=your-discord-bot-token
Run the Bot

Execute the following command to start the bot:

bash
Copy code
python main.py
Commands
?jobs [num_jobs]: Get a list of the most recent job postings (default: 5).
?swe [num_jobs]: Get a list of the most recent Software Engineering Internships (default: 5).
?fullstack [num_jobs]: Get a list of the most recent Full Stack, Backend, and Front End Internships (default: 5).
?it [num_jobs]: Get a list of the most recent IT-related Internships (default: 5).
?recent: Get a list of jobs posted in the last 48 hours.
?src: Get a link to the source of the job data.
?git: Get a link to the bot's source code.
Example Usage
bash
Copy code
?jobs 10
This command fetches the 10 most recent job postings and sends them to the channel.

Development
Feel free to contribute to this project by creating issues or submitting pull requests. For any questions or suggestions, open an issue or contact me directly.

