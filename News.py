from fastapi import FastAPI, BackgroundTasks
import feedparser
import asyncio
from transformers import pipeline
from datetime import datetime
import streamlit as st
import uvicorn
from contextlib import asynccontextmanager

app = FastAPI()

RSS_FEEDS = [
    "https://www.theguardian.com/international/rss",
    "https://www.dailymail.co.uk/news/index.rss",
    "https://www.independent.co.uk/news/world/rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

news_cache = []
summarizer = pipeline("summarization", model="Falconsai/text_summarization")

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
                "content": entry.summary,
            }
            if news_item["content"]:
                summary = summarizer(news_item["content"])
                news_item["summary"] = summary[0]["summary_text"]
            else:
                news_item["summary"] = "No content available"
            
            news_list.append(news_item)
    
    news_cache = news_list

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

@app.get("/news")
def get_news():
    return {"news": news_cache}

if __name__ == "__main__":
    st.title("News API Host")
    st.write("Running FastAPI...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
