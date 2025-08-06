from langchain_community.document_loaders import WebBaseLoader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

from fastmcp import FastMCP
from dotenv import load_dotenv
import json
import bs4
load_dotenv()

mcp = FastMCP("Employees MCP HTTP Agent")

def load_page_with_scroll(url, wait_time=5, scroll_pause=2):
    """Load page with waiting and scrolling functionality"""
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--log-level=3")  # Suppress most logs
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Load the page
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Scroll down to load more content
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content to load
            time.sleep(scroll_pause)
            
            # Calculate new scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # If height is the same, we've reached the bottom
            if new_height == last_height:
                break
                
            last_height = new_height
        
        # Get the final page source
        page_source = driver.page_source
        return page_source
        
    finally:
        driver.quit()

@mcp.tool(description="Получение списка последних новостей", name="latest_news_details")
def get_employee_detail() -> str:
    """Получение списка последних новостей с сайта"""
    url = "https://tengrinews.kz"
    
    # Load page with waiting and scrolling
    page_source = load_page_with_scroll(url, wait_time=10, scroll_pause=3)
    
    # Parse the HTML content
    soup = bs4.BeautifulSoup(page_source, 'html.parser')
    
    # Extract news items
    news_items = []
    news_elements = soup.find_all(class_=["main-news_super_item", "main-news_super_item_title", "main-news_super_item_meta"])
    
    for element in news_elements:
        # Extract text content
        text_content = element.get_text(strip=True)
        
        # Extract links safely
        link_element = element.find('a')
        url = None
        if link_element:
            url = link_element.get('href')
            if url and url.startswith('/'):
                url = f"https://tengrinews.kz{url}"
        
        if text_content:
            news_items.append({
                "content": text_content,
                "urls": url
            })
    
    # Convert to JSON
    result = {
        "news_items": news_items,
        "total_count": len(news_items)
    }
    
    json_string = json.dumps(result, ensure_ascii=False, indent=4)
    return json_string 

@mcp.tool(description="Получение списка туров во Вьетнам", name="get_hot_tours_vietnam")
def get_vietnam_tours() -> str:
    """Получение списка горящих туров с сайта"""
    url = "https://ht.kz/tours/vietnam-from-almaty"
    
    # Load page with waiting and scrolling
    page_source = load_page_with_scroll(url, wait_time=10, scroll_pause=3)
    
    # Parse the HTML content
    soup = bs4.BeautifulSoup(page_source, 'html.parser')
    
    # Extract tour items
    tour_items = []
    tour_elements = soup.find_all(class_=["ng-row", "ng-content", "ng-prices","href"])
    print(tour_elements)
    
    for element in tour_elements:
        # Extract text content
        text_content = element.get_text(strip=True)
        
        # Extract links safely
        link_element = element.find('a')
        url = None
        if link_element:
            url = link_element.get('href')
            if url and url.startswith('/'):
                url = f"https://ht.kz{url}"
        
        if text_content:
            tour_items.append({
                "content": text_content,
                "urls": url
            })
    
    # Convert to JSON
    result = {
        "tour_items": tour_items,
        "total_count": len(tour_items)
    }
    
    json_string = json.dumps(result, ensure_ascii=False, indent=4)
    return json_string 

@mcp.tool(description="Получение списка туров в Турцию", name="get_hot_tours_tyrkey")
def get_tyrkey_tours() -> str:
    """Получение списка горящих туров с сайта"""
    url = "https://ht.kz/tours/turkey-from-almaty"
    
    # Load page with waiting and scrolling
    page_source = load_page_with_scroll(url, wait_time=10, scroll_pause=3)
    
    # Parse the HTML content
    soup = bs4.BeautifulSoup(page_source, 'html.parser')
    
    # Extract tour items
    tour_items = []
    tour_elements = soup.find_all(class_=["ng-row", "ng-content", "ng-prices","href"])
    print(tour_elements)
    
    for element in tour_elements:
        # Extract text content
        text_content = element.get_text(strip=True)
        
        # Extract links safely
        link_element = element.find('a')
        url = None
        if link_element:
            url = link_element.get('href')
            if url and url.startswith('/'):
                url = f"https://ht.kz{url}"
        
        if text_content:
            tour_items.append({
                "content": text_content,
                "urls": url
            })
    
    # Convert to JSON
    result = {
        "tour_items": tour_items,
        "total_count": len(tour_items)
    }
    
    json_string = json.dumps(result, ensure_ascii=False, indent=4)
    return json_string 

@mcp.tool(description="Получение списка туров в Тайланд", name="get_hot_tours_thailand")
def get_hailand_tours() -> str:
    """Получение списка горящих туров с сайта"""
    url = "https://ht.kz/tours/thailand-from-almaty"
    
    # Load page with waiting and scrolling
    page_source = load_page_with_scroll(url, wait_time=10, scroll_pause=3)
    
    # Parse the HTML content
    soup = bs4.BeautifulSoup(page_source, 'html.parser')
    
    # Extract tour items
    tour_items = []
    tour_elements = soup.find_all(class_=["ng-row", "ng-content", "ng-prices","href"])
    print(tour_elements)
    
    for element in tour_elements:
        # Extract text content
        text_content = element.get_text(strip=True)
        
        # Extract links safely
        link_element = element.find('a')
        url = None
        if link_element:
            url = link_element.get('href')
            if url and url.startswith('/'):
                url = f"https://ht.kz{url}"
        
        if text_content:
            tour_items.append({
                "content": text_content,
                "urls": url
            })
    
    # Convert to JSON
    result = {
        "tour_items": tour_items,
        "total_count": len(tour_items)
    }
    
    json_string = json.dumps(result, ensure_ascii=False, indent=4)
    return json_string 

@mcp.tool(description="Получение списка туров на Мальдивы", name="get_hot_tours_maldives")
def get_maldives_tours() -> str:
    """Получение списка горящих туров с сайта"""
    url = "https://ht.kz/tours/maldives-from-almaty"
    
    # Load page with waiting and scrolling
    page_source = load_page_with_scroll(url, wait_time=10, scroll_pause=3)
    
    # Parse the HTML content
    soup = bs4.BeautifulSoup(page_source, 'html.parser')
    
    # Extract tour items
    tour_items = []
    tour_elements = soup.find_all(class_=["ng-row", "ng-content", "ng-prices","href"])
    print(tour_elements)
    
    for element in tour_elements:
        # Extract text content
        text_content = element.get_text(strip=True)
        
        # Extract links safely
        link_element = element.find('a')
        url = None
        if link_element:
            url = link_element.get('href')
            if url and url.startswith('/'):
                url = f"https://ht.kz{url}"
        
        if text_content:
            tour_items.append({
                "content": text_content,
                "urls": url
            })
    
    # Convert to JSON
    result = {
        "tour_items": tour_items,
        "total_count": len(tour_items)
    }
    
    json_string = json.dumps(result, ensure_ascii=False, indent=4)
    return json_string 

@mcp.tool(description="Туристический календарь путешествий", name="get_tour_calendar")
def get_tour_calendar() -> str:
    """Получение туристического календаря с сайта"""
    url = "https://okeanturov.ru/advices/travel-calendar/"
    
    # Load page with waiting and scrolling
    page_source = load_page_with_scroll(url, wait_time=10, scroll_pause=3)
    
    # Parse the HTML content
    soup = bs4.BeautifulSoup(page_source, 'html.parser')
    
    # Find the content div
    content_div = soup.find('div', id='content')
    
    if not content_div:
        return json.dumps({"error": "Content div not found"}, ensure_ascii=False, indent=4)
    
    # Extract structured information
    calendar_info = {
        "title": "",
        "description": [],
        "monthly_recommendations": []
    }
    
    # Extract title
    title_element = content_div.find('h1')
    if title_element:
        calendar_info["title"] = title_element.get_text(strip=True)
    
    # Extract description paragraphs (before h3 elements)
    for element in content_div.children:
        if element.name == 'p':
            text = element.get_text(strip=True)
            if text and not any(month in text.lower() for month in ['январе', 'феврале', 'марте', 'апреле', 'мае', 'июне', 'июле', 'августе', 'сентябре', 'октябре', 'ноябре', 'декабре']):
                calendar_info["description"].append(text)
        elif element.name == 'h3':
            break
    
    # Extract monthly recommendations
    current_month = None
    current_description = []
    
    for element in content_div.find_all(['h3', 'p']):
        if element.name == 'h3':
            # Save previous month if exists
            if current_month:
                calendar_info["monthly_recommendations"].append({
                    "month": current_month,
                    "description": " ".join(current_description),
                    "links": []
                })
            
            # Start new month
            current_month = element.get_text(strip=True)
            current_description = []
            
        elif element.name == 'p' and current_month:
            # Add description for current month
            text = element.get_text(strip=True)
            if text:
                current_description.append(text)
                
                # Extract links from this paragraph
                links = []
                for link in element.find_all('a'):
                    href = link.get('href')
                    link_text = link.get_text(strip=True)
                    if href:
                        if href.startswith('/'):
                            href = f"https://okeanturov.ru{href}"
                        links.append({
                            "text": link_text,
                            "url": href
                        })
                
                # Update the last month's links if we have any
                if links and calendar_info["monthly_recommendations"]:
                    calendar_info["monthly_recommendations"][-1]["links"].extend(links)
    
    # Add the last month if exists
    if current_month:
        calendar_info["monthly_recommendations"].append({
            "month": current_month,
            "description": " ".join(current_description),
            "links": []
        })
    
    json_string = json.dumps(calendar_info, ensure_ascii=False, indent=4)
    return json_string 

@mcp.tool(description="Куда поехать в разные сезоны", name="get_travel_season")
def get_travel_season():
    """Куда поехать в разные сезоны"""
    url = "https://www.travelv.ru/statya.php?id=56"
    
    # Load page with waiting and scrolling
    page_source = load_page_with_scroll(url, wait_time=10, scroll_pause=3)
    
    # Parse the HTML content
    soup = bs4.BeautifulSoup(page_source, 'html.parser')
    
    # Extract tour items
    tour_items = []
    tour_elements = soup.find_all(class_=["text_big mt-5 mb-5"])
    print(tour_elements)
    
    for element in tour_elements:
        # Extract text content
        text_content = element.get_text(strip=True)
        
        # Extract links safely
        link_element = element.find('a')
        url = None
        if link_element:
            url = link_element.get('href')
            if url and url.startswith('/'):
                url = f"https://ht.kz{url}"
        
        if text_content:
            tour_items.append({
                "content": text_content,
                "urls": url
            })
    
    # Convert to JSON
    result = {
        "tour_items": tour_items,
        "total_count": len(tour_items)
    }
    
    json_string = json.dumps(result, ensure_ascii=False, indent=4)
    return json_string 


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=9010) 