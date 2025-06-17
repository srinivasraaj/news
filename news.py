import nest_asyncio 
nest_asyncio.apply()

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

# Function to extract Telugu + time marker entries
async def fetch_time_tagged_telugu(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(5000)

        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')

        timestamp_regex = re.compile(r"\[\d{1,2}:\d{2}\]")
        telugu_regex = re.compile(r"[\u0C00-\u0C7F]")

        entries = []

        for tag in soup.find_all(['p', 'h1', 'h2', 'div', 'span']):
            raw_text = tag.get_text(strip=True)
            if not raw_text:
                continue

            timestamps = timestamp_regex.findall(raw_text)
            if timestamps:
                split_text = timestamp_regex.split(raw_text)
                split_text = [t.strip() for t in split_text if t.strip()]
                for i, sentence in enumerate(split_text):
                    if i < len(timestamps) and telugu_regex.search(sentence):
                        entries.append({
                            "time": timestamps[i],
                            "text": sentence
                        })
            elif telugu_regex.search(raw_text):
                entries.append({
                    "time": "",
                    "text": raw_text
                })

        await browser.close()
        return entries

# Example usage
url = "https://www.eenadu.net/telugu-news"
results = asyncio.get_event_loop().run_until_complete(fetch_time_tagged_telugu(url))

# Split logic on "..!", "..", "!" into new lines
split_pattern = re.compile(r"(?:\.\.!\s*|\.\.\s*|!\s*)")
final_lines = []

for entry in results:
    combined = f"{entry['time']} {entry['text']}".strip() if entry["time"] else entry["text"]
    parts = [line.strip() for line in split_pattern.split(combined) if line.strip()]
    final_lines.extend(parts)

# Print and save
#for line in final_lines:
#    print(line)

import os
if os.path.exists("output.txt"):
    os.remove("output.txt")

with open("output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(final_lines))
