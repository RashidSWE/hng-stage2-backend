import os
from datetime import datetime
import matplotlib.pyplot as plt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from ..models.Country import Country

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)
IMAGE_PATH = os.path.join(CACHE_DIR, "summary.png")

async def generate_summary_image(db: AsyncSession):
    """ Query total countries """
    total_query = await db.execute(select(func.count(Country.id)))
    total_countries = total_query.scalar_one()

    """ Query top 5 gdp """
    top_query = await db.execute(
        select(Country.name, Country.estimated_gdp)
        .order_by(desc(Country.estimated_gdp))
        .limit(5)
    )
    top_countries = top_query.all()

    """ get last refresh """
    last_refresh_query = await db.execute(select(func.max(Country.last_refreshed_at)))
    last_refreshed = last_refresh_query.scalar_one()

    """ plot the data """
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#f5f5f5")

    # Title
    plt.title("Country Summary", fontsize=18, fontweight="bold")

    summary_text = (
        f"Total Countries: {total_countries}\n"
        f"Last Refresh: {last_refreshed.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"Top 5 countries by Estimated GDP:\n"
    )
    for i, (name, gdp) in enumerate(top_countries, start=1):
        summary_text += f"{i}. {name} — {gdp:,.0f}\n"
    
    """ Display text on image"""
    plt.axis("off")
    plt.text(0.05, 0.95, summary_text, fontsize=13, va="top", fontfamily="monospace")

    """save image"""
    plt.tight_layout()
    plt.savefig(IMAGE_PATH)
    plt.close()

    return IMAGE_PATH