import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append('.')

from app.scraper.scraper import scrape_with_retry, PaywallError

async def test_url(url: str):
    print(f"\nTesting URL: {url}")
    print("-" * 80)
    
    try:
        result = await scrape_with_retry(url)
        
        if result["error"]:
            print(f"❌ Error: {result['error']}")
            return
        
        print("✅ Scraping successful!")
        
        # Display metadata
        print("\nMetadata:")
        print("-" * 40)
        metadata = result["metadata"]
        
        # Basic metadata
        basic_fields = ['title', 'description', 'author', 'date']
        for field in basic_fields:
            if metadata.get(field):
                print(f"{field.capitalize()}: {metadata[field]}")
        
        # Keywords and tags
        if metadata.get('keywords'):
            print(f"Keywords: {', '.join(metadata['keywords'])}")
        if metadata.get('tags'):
            print(f"Tags: {', '.join(metadata['tags'])}")
        if metadata.get('category'):
            print(f"Category: {metadata['category']}")
            
        # Reading stats
        if metadata.get('word_count'):
            print(f"\nReading Stats:")
            print(f"Word count: {metadata['word_count']}")
            print(f"Reading time: {metadata['reading_time_minutes']} minutes")
            
        # Additional metadata
        if metadata.get('language'):
            print(f"Language: {metadata['language']}")
        if metadata.get('site_name'):
            print(f"Site: {metadata['site_name']}")
        
        # Content preview
        print("\nContent Preview:")
        print("-" * 40)
        content_preview = result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"]
        print(content_preview)
        print("\n")
        
    except PaywallError as e:
        print(f"⚠️ Paywall detected: {str(e)}")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

async def main():
    # Test URLs representing different types of content
    urls = [
        # Blog post
        "https://blog.langchain.dev/langgraph-cloud/",
        
        # News article (likely paywalled)
        "https://www.nytimes.com/2024/02/20/technology/anthropic-claude-3-ai.html",
        
        # News article (non-paywalled)
        "https://techcrunch.com/2024/02/20/anthropic-introduces-claude-3-claims-its-most-capable-ai-model-yet/",
        
        # Documentation
        "https://docs.python.org/3/tutorial/introduction.html",
        
        # Medium article
        "https://medium.com/@martin_hotell/10-typescript-pro-tips-patterns-with-or-without-react-5799488d6680",
        
        # GitHub README
        "https://github.com/langchain-ai/langchain/blob/master/README.md",
        
        # WordPress blog
        "https://learnwithhasan.com/blog/replace-wordpress-plugins-ai-code-snippets/"
    ]
    
    for url in urls:
        try:
            await test_url(url)
        except Exception as e:
            print(f"❌ Test failed for {url}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 