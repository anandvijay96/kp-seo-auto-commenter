import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape_page(url: str) -> str:
    """
    Asynchronously scrapes the main content of a given URL using Playwright.

    Args:
        url: The URL of the page to scrape.

    Returns:
        The extracted text content of the article.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")

            html_content = await page.content()
            await browser.close()

            soup = BeautifulSoup(html_content, "html.parser")

            # Find the main content, trying common tags, falling back to the body
            main_content = soup.find("article") or soup.find("main") or soup.body

            if main_content:
                # Remove script, style, nav, header, and footer elements
                for element in main_content(["script", "style", "nav", "header", "footer"]):
                    element.decompose()
                
                # Get text and clean up whitespace
                text = main_content.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                return text
            else:
                return "Error: Could not find the main content of the page."

    except Exception as e:
        print(f"An error occurred while scraping {url}: {e}")
        return f"Error: Could not scrape the page. Details: {e}"

# Example for standalone testing
async def main():
    # Test URL - replace with any blog post you want to test
    test_url = "https://blog.langchain.dev/langgraph-cloud/"
    print(f"Scraping: {test_url}\n")
    content = await scrape_page(test_url)
    print("--- SCRAPED CONTENT ---")
    print(content)
    print("\n--- END OF CONTENT ---")

if __name__ == "__main__":
    asyncio.run(main())