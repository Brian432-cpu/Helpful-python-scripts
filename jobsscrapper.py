import requests
from bs4 import BeautifulSoup
import csv
import datetime
import json

# --- CONFIG ---
OUTPUT_FILE = 'job_results.csv'

# --- SCRAPER FUNCTIONS ---

def scrape_linkedin(keyword):
    print('[*] Scraping LinkedIn...')
    jobs = []
    search_url = f'https://www.linkedin.com/jobs/search?keywords={keyword.replace(" ", "%20")}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        listings = soup.find_all('div', class_='base-card')
        for job in listings:
            title = job.find('h3')
            company = job.find('h4')
            link = job.find('a', href=True)
            if title and company and link:
                jobs.append({
                    'Job Title': title.text.strip(),
                    'Company / Poster': company.text.strip(),
                    'Job Type': 'N/A',
                    'Source': 'LinkedIn',
                    'URL': link['href']
                })
    except Exception as e:
        print(f'[!] LinkedIn scraping failed: {e}')
    return jobs

def scrape_reddit(keyword):
    print('[*] Scraping Reddit...')
    jobs = []
    url = f'https://www.reddit.com/search.json?q={keyword}+jobs&sort=new'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        for post in data['data']['children']:
            post_data = post['data']
            jobs.append({
                'Job Title': post_data['title'],
                'Company / Poster': post_data['author'],
                'Job Type': 'N/A',
                'Source': 'Reddit',
                'URL': 'https://reddit.com' + post_data['permalink']
            })
    except Exception as e:
        print(f'[!] Reddit scraping failed: {e}')
    return jobs

def scrape_greenhouse(keyword):
    print('[*] Scraping Greenhouse.io...')
    jobs = []
    try:
        res = requests.get(f'https://api.greenhouse.io/v1/boards/{keyword}/jobs', timeout=10)
        if res.status_code == 200:
            data = res.json()
            for job in data.get('jobs', []):
                jobs.append({
                    'Job Title': job.get('title', 'N/A'),
                    'Company / Poster': job.get('department', {}).get('name', 'N/A'),
                    'Job Type': 'N/A',
                    'Source': 'Greenhouse',
                    'URL': job.get('absolute_url', '')
                })
    except Exception as e:
        print(f'[!] Greenhouse scraping failed: {e}')
    return jobs

def scrape_remoteok(keyword):
    print('[*] Scraping RemoteOK...')
    jobs = []
    url = f'https://remoteok.com/api'
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        for job in data:
            if isinstance(job, dict) and keyword.lower() in job.get('position', '').lower():
                jobs.append({
                    'Job Title': job.get('position', 'N/A'),
                    'Company / Poster': job.get('company', 'N/A'),
                    'Job Type': job.get('type', 'Remote'),
                    'Source': 'RemoteOK',
                    'URL': job.get('url', '')
                })
    except Exception as e:
        print(f'[!] RemoteOK scraping failed: {e}')
    return jobs

def scrape_weworkremotely(keyword):
    print('[*] Scraping WeWorkRemotely...')
    jobs = []
    try:
        res = requests.get(f'https://weworkremotely.com/remote-jobs/search?term={keyword}', timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        listings = soup.select('section.jobs article li a')
        for link in listings:
            title = link.text.strip()
            href = 'https://weworkremotely.com' + link['href']
            jobs.append({
                'Job Title': title,
                'Company / Poster': 'Unknown',
                'Job Type': 'Remote',
                'Source': 'We Work Remotely',
                'URL': href
            })
    except Exception as e:
        print(f'[!] WeWorkRemotely scraping failed: {e}')
    return jobs

def scrape_upwork(keyword):
    print('[*] Scraping Upwork...')
    jobs = []
    try:
        res = requests.get(f'https://www.upwork.com/nx/jobs/search/?q={keyword}', timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        listings = soup.find_all('section', {'data-test': 'job-tile-list'})
        for job in listings:
            title = job.find('a')
            if title:
                jobs.append({
                    'Job Title': title.text.strip(),
                    'Company / Poster': 'Client',
                    'Job Type': 'Freelance',
                    'Source': 'Upwork',
                    'URL': 'https://www.upwork.com' + title['href']
                })
    except Exception as e:
        print(f'[!] Upwork scraping failed: {e}')
    return jobs

# --- MAIN ---
def main():
    keyword = input('Enter job keyword to search: ').strip()
    all_jobs = []

    for scraper in [scrape_linkedin, scrape_reddit, scrape_greenhouse, scrape_remoteok, scrape_weworkremotely, scrape_upwork]:
        results = scraper(keyword)
        all_jobs.extend(results)

    print(f'[*] Total jobs found: {len(all_jobs)}')

    if all_jobs:
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Job Title', 'Company / Poster', 'Job Type', 'Source', 'URL'])
            writer.writeheader()
            writer.writerows(all_jobs)
        print(f'[+] Results saved to {OUTPUT_FILE}')
    else:
        print('[!] No jobs found.')

if __name__ == '__main__':
    main()
