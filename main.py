from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import feedparser
import asyncio
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager

app = FastAPI(title="News Fetch API", description="Fetches latest news from RSS feeds efficiently.")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RSS_FEEDS = [
    "https://www.theguardian.com/international/rss",
    "https://www.dailymail.co.uk/news/index.rss",
    "https://www.independent.co.uk/news/world/rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

news_cache = []

def fetch_news():
    global news_cache
    news_list = []
    
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            news_item = {
                "headline": entry.title,
                "link": entry.link,
                "cover_image": entry.media_content[0]['url'] if 'media_content' in entry else None,
                "published": entry.published if hasattr(entry, 'published') else str(datetime.now()),
                "content": entry.summary if hasattr(entry, 'summary') else "No content available",
            }
            news_list.append(news_item)
    
    news_cache = news_list
    print("Fetched News:", news_cache)  # Print fetched news for debugging

async def update_news():
    while True:
        fetch_news()
        await asyncio.sleep(300)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(update_news())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/news", summary="Get Latest News", description="Fetches the latest news articles from various sources.")
def get_news():
    return {"news": news_cache}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
