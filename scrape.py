import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime

def setup_driver():
    print("Setting up Chrome browser...")
    chrome_driver_path = "./chromedriver/chromedriver.exe"
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-proxy-server")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/122.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    return webdriver.Chrome(service=Service(chrome_driver_path), options=options)


def scrape_dailystar():
    driver = setup_driver()
    articles = []
    
    try:
        driver.get("https://www.thedailystar.net/")
        print("Successfully opened The Daily Star")
        time.sleep(3)

        # Parsing HTML and extracting all relevant links to Bangladesh
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_links = soup.find_all('a', href=True)
        bd_news_links = [a['href'] for a in all_links if a['href'].startswith('/news/bangladesh/')]

        # Removing duplicates 
        seen = set()
        unique_links = []
        for link in bd_news_links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)

        print(f"Found {len(unique_links)} unique Bangladesh news links.")

        
        for link in unique_links[:20]:
            full_url = f"https://www.thedailystar.net{link}"
            try:
                driver.get(full_url)
                time.sleep(2)

                article_soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Extracting the headline (h1 tag)
                title_tag = article_soup.find('h1')
                title = title_tag.text.strip() if title_tag else "No title found"

                # Extracting article content (div with class 'pb-20 clearfix')
                content_div = article_soup.find('div', class_='pb-20 clearfix')
                if content_div:
                    paragraphs = content_div.find_all('p')
                    content = ' '.join(p.text.strip() for p in paragraphs)
                else:
                    content = "No content found"

                articles.append({
                    "title": title,
                    "url": full_url,
                    "content": content,
                    "source": "The Daily Star",
                    "date": datetime.now().strftime("%Y-%m-%d")
                })

                print(f"Scraped: {title}")
            except Exception as e:
                print(f"Error processing article {full_url}: {e}")

    except Exception as e:
        print(f"Error accessing The Daily Star: {e}")
    finally:
        driver.quit()
        print("Browser closed.")
    
    return articles

def scrape_prothomalo_en():
    driver = setup_driver()
    articles = []
    
    try:
        driver.get("https://en.prothomalo.com/")
        print("Successfully opened Prothom Alo English")
        time.sleep(3)

        # Parsing HTML and extracting all relevant links to Bangladesh
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_links = soup.find_all('a', href=True)
        bd_news_links = [a['href'] for a in all_links if a['href'].startswith('https://en.prothomalo.com/bangladesh/')]

        # Removing duplicates 
        seen = set()
        unique_links = []
        for link in bd_news_links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)

        print(f"Found {len(unique_links)} unique Bangladesh news links.")

        
        for url in unique_links[:20]:
        
            try:
                driver.get(url)
                time.sleep(2)

                article_soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Extracting the headline (h1 tag)
                title_tag = article_soup.find('h1')
                title = title_tag.text.strip() if title_tag else "No title found"

                # Extracting article content (div with class 'story-element story-element-text')
                content_divs = article_soup.find_all('div', class_='story-element story-element-text')
                if content_divs:
                    content_parts = []
                    for div in content_divs:
                        paragraphs = div.find_all('p')
                        for p in paragraphs:
                            content_parts.append(p.text.strip())
                    content = ' '.join(content_parts)
                else:
                    content = "No content found"


                articles.append({
                    "title": title,
                    "url": url,
                    "content": content,
                    "source": "Prothom Alo English",
                    "date": datetime.now().strftime("%Y-%m-%d")
                })

                print(f"Scraped: {title}")
            except Exception as e:
                print(f"Error processing article {url}: {e}")

    except Exception as e:
        print(f"Error accessing Prothom Alo English: {e}")
    finally:
        driver.quit()
        print("Browser closed.")
    
    return articles


def save_articles(articles):
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    filename = f"{data_dir}/news_articles_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    
    print(f"Saved {len(articles)} articles to {filename}")
    return filename

def scrape_all_news():
    print("Starting news scraping...")
    articles = []
    
    # May add more sources in the future
    articles.extend(scrape_dailystar())
    articles.extend(scrape_prothomalo_en())

    print(f"Total articles scraped: {len(articles)}")
    if articles:
        return save_articles(articles)
    else:
        print("No articles were scraped.")
        return None

if __name__ == "__main__":
    scrape_all_news()