import asyncio
from typing import Dict, Optional, Union
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import re
from datetime import datetime
import readtime

class ScraperError(Exception):
    """Custom exception for scraper errors"""
    pass

class PaywallError(ScraperError):
    """Error for paywalled content"""
    pass

async def scrape_with_retry(url: str, max_retries: int = 3, initial_timeout: int = 30000) -> Dict[str, Union[str, dict]]:
    """Retry scraping with increasing timeouts."""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            timeout = initial_timeout * (attempt + 1)  # Increase timeout with each retry
            return await scrape_page(url, timeout=timeout)
        except PlaywrightTimeout as e:
            last_error = e
            print(f"Attempt {attempt + 1} failed with timeout {timeout}ms. Retrying...")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            last_error = e
            if "paywall" in str(e).lower():
                raise PaywallError(f"Content is behind a paywall: {str(e)}")
            print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
            await asyncio.sleep(2 ** attempt)
    
    raise ScraperError(f"Failed after {max_retries} attempts. Last error: {str(last_error)}")

async def scrape_page(url: str, timeout: int = 30000) -> Dict[str, Union[str, dict]]:
    """
    Asynchronously scrapes content and metadata from a given URL using Playwright.

    Args:
        url: The URL of the page to scrape.

    Returns:
        Dict containing:
        - content: The main article content
        - metadata: Dict with title, description, author, date, etc.
        - error: Error message if any (None if successful)
    """
    try:
        async with async_playwright() as p:
            # Launch chromium with optimized settings
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                    '--disable-notifications',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-breakpad',
                    '--disable-component-extensions-with-background-pages',
                    '--disable-extensions',
                    '--disable-features=TranslateUI,BlinkGenPropertyTrees',
                    '--disable-ipc-flooding-protection',
                    '--disable-renderer-backgrounding',
                    '--enable-features=NetworkService,NetworkServiceInProcess',
                ]
            )
            
            context = await browser.new_context(
                viewport={"width": 1280, "height": 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                bypass_csp=True  # Bypass Content Security Policy
            )
            
            page = await context.new_page()
            page.set_default_timeout(timeout)

            try:
                # Navigate and wait for content
                response = await page.goto(url, wait_until="networkidle")
                
                # Check for common paywall indicators
                if await detect_paywall(page):
                    raise PaywallError("Content appears to be behind a paywall")
                
                await asyncio.sleep(2)  # Wait for dynamic content
                
                # Get page content and metadata
                html_content = await page.content()
                metadata = await extract_metadata(page)
                
                # Extract main content
                content = await extract_content(html_content)
                
                if not content:
                    raise ScraperError("No main content found")
                
                # Add additional metadata
                metadata.update(await extract_additional_metadata(page, content))

                return {
                    "content": content,
                    "metadata": metadata,
                    "error": None
                }

            except PlaywrightTimeout:
                raise ScraperError("Page load timeout")
            finally:
                await context.close()
                await browser.close()

    except Exception as e:
        error_msg = f"Failed to scrape {url}: {str(e)}"
        print(error_msg)  # Log the error
        return {
            "content": "",
            "metadata": {},
            "error": error_msg
        }

async def detect_paywall(page) -> bool:
    """Detect if content is behind a paywall."""
    paywall_indicators = [
        # Common paywall text
        "subscribe to continue",
        "subscription required",
        "premium content",
        "subscribe now",
        "premium article",
        "members only",
        # Common paywall elements
        ".paywall",
        ".subscription-required",
        "#paywall",
        ".premium-content",
        ".membership-required"
    ]
    
    # Check for paywall text
    page_text = await page.text_content("body")
    if any(indicator.lower() in page_text.lower() for indicator in paywall_indicators if not indicator.startswith(".")):
        return True
    
    # Check for paywall elements
    for selector in paywall_indicators:
        if selector.startswith(".") or selector.startswith("#"):
            try:
                element = await page.query_selector(selector)
                if element:
                    return True
            except:
                continue
    
    return False

async def extract_metadata(page) -> dict:
    """Extract comprehensive metadata from the page."""
    metadata = {}
    
    # Basic metadata
    metadata['title'] = await page.title()
    metadata['url'] = page.url
    
    # Extract meta tags
    meta_tags = await page.evaluate("""() => {
        const metas = document.getElementsByTagName('meta');
        const data = {};
        for (let i = 0; i < metas.length; i++) {
            if (metas[i].getAttribute('name')) {
                data[metas[i].getAttribute('name')] = metas[i].getAttribute('content');
            } else if (metas[i].getAttribute('property')) {
                data[metas[i].getAttribute('property')] = metas[i].getAttribute('content');
            }
        }
        return data;
    }""")
    
    # Process common meta tags
    metadata['description'] = meta_tags.get('description') or meta_tags.get('og:description')
    metadata['author'] = (
        meta_tags.get('author') or 
        meta_tags.get('article:author') or 
        meta_tags.get('og:article:author')
    )
    
    # Extract and normalize date
    date = (
        meta_tags.get('article:published_time') or 
        meta_tags.get('date') or 
        meta_tags.get('article:modified_time') or
        meta_tags.get('og:article:published_time')
    )
    if date:
        try:
            # Try to parse and format the date consistently
            parsed_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            metadata['date'] = parsed_date.isoformat()
        except:
            metadata['date'] = date
    
    # Extract additional meta tags
    metadata['keywords'] = meta_tags.get('keywords', '').split(',') if meta_tags.get('keywords') else []
    metadata['category'] = meta_tags.get('article:section') or meta_tags.get('category')
    metadata['tags'] = [
        tag.strip() 
        for tag in (meta_tags.get('article:tag', '') or meta_tags.get('news_keywords', '')).split(',')
        if tag.strip()
    ]
    
    return metadata

async def extract_additional_metadata(page, content: str) -> dict:
    """Extract additional metadata like reading time, word count, etc."""
    additional_metadata = {}
    
    # Calculate reading time and word count
    result = readtime.of_text(content)
    additional_metadata['reading_time_seconds'] = result.seconds
    additional_metadata['reading_time_minutes'] = round(result.seconds / 60, 1)
    additional_metadata['word_count'] = len(content.split())
    
    # Extract language (if available)
    try:
        lang = await page.evaluate('document.documentElement.lang')
        if lang:
            additional_metadata['language'] = lang
    except:
        pass
    
    # Extract site name
    try:
        site_name = await page.evaluate("""() => {
            const el = document.querySelector('meta[property="og:site_name"]');
            return el ? el.getAttribute('content') : null;
        }""")
        if site_name:
            additional_metadata['site_name'] = site_name
    except:
        pass
    
    return additional_metadata

async def extract_content(html: str) -> str:
    """Extract and clean main content from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove unwanted elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 
                        'noscript', 'aside', 'form', 'button', 'input', 'meta',
                        'link', 'svg', 'path', 'symbol', 'img']):
        element.decompose()

    # Try multiple strategies to find main content
    content_element = (
        soup.find('article') or
        soup.find('main') or
        soup.find(class_=re.compile(r'(article|post|content|entry)[-_]?(content|body|text)')) or
        soup.find(id=re.compile(r'(article|post|content|entry)[-_]?(content|body|text)')) or
        soup.find('div', class_=lambda x: x and any(term in x.lower() for term in ['article', 'post', 'content', 'entry'])) or
        soup.body
    )

    if not content_element:
        return ""

    # Clean up the content
    paragraphs = []
    for p in content_element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote']):
        text = p.get_text().strip()
        if text and len(text) > 20:  # Filter out short snippets
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            # Remove common advertisement text
            if not any(ad_text in text.lower() for ad_text in ['advertisement', 'sponsored', 'promotion']):
                paragraphs.append(text)

    # Join paragraphs with proper spacing
    content = '\n\n'.join(paragraphs)
    
    # Remove duplicate newlines and clean up spacing
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()
    
    return content

# Example for standalone testing
async def main():
    test_url = "https://blog.langchain.dev/langgraph-cloud/"
    print(f"Scraping: {test_url}\n")
    
    result = await scrape_page(test_url)
    
    if result["error"]:
        print("Error:", result["error"])
    else:
        print("--- METADATA ---")
        for key, value in result["metadata"].items():
            print(f"{key}: {value}")
        
        print("\n--- CONTENT ---")
        print(result["content"])
    print("\n--- END OF CONTENT ---")

if __name__ == "__main__":
    asyncio.run(main())