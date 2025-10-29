from fastapi import APIRouter, HTTPException, status, Depends, Query
from ..utils.helper import fetch_countries, fetch_countries_with_rates
from ..models.Country import Country
from ..config.Config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from typing import Optional
from ..utils.image_generator import generate_summary_image
from fastapi.responses import FileResponse
import os


router = APIRouter()
CACHE_DIR = "cache"
IMAGE_PATH = os.path.join(CACHE_DIR, "summary.png")


@router.post("/countries/refresh")
async def refresh_data(db: AsyncSession = Depends(get_session)):
    try:
        countries_data = await fetch_countries_with_rates()

        if not countries_data:
            raise HTTPException(status_code=404, detail="No country data found")
        
        existing_countries_result = await db.execute(select(Country))
        existing_countries = existing_countries_result.scalars().all()

        # Convert to dict for O(1) lookup
        existing_map = {c.name: c for c in existing_countries}

        new_countries = []
        for item in countries_data:
            name = item["name"]
            if name in existing_map:
                # Update existing record
                existing = existing_map[name]
                for key, value in item.items():
                    setattr(existing, key, value)
            else:
                # Add new country
                new_countries.append(Country(**item))

        if new_countries:
            db.add_all(new_countries)
        
        await db.commit()
        await generate_summary_image(db)

        return {"message": "countries refreshed successfully and image created"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error refreshing countries: {e} ")


@router.get("/countries")
async def get_countires_data(
    region: Optional[str] = Query(None, description="Filter by region"),
    currency: Optional[str] = Query(None, description="Filter by currency"),
    sort: Optional[str] = Query(None, description="filter by gdp_asc or gdp_desc"),
    db: AsyncSession = Depends(get_session), 

):
    query = select(Country)

    if region:
        query = query.where(Country.region == region)
    
    if currency:
        query = query.where(Country.currency_code == currency)
    
    if sort:
        if sort.lower() == "gdp_asc":
            query = query.order_by(Country.estimated_gdp.asc())
        elif sort.lower() == "gdp_desc":
            query = query.order_by(Country.estimated_gdp.desc())
    
    result = await db.execute(query)
    countries = result.scalars().all()

    return countries

@router.get("/countries/image")
async def summary_image():
    image_path = os.path.abspath(IMAGE_PATH)
    print("Checking file:", os.path.abspath(image_path))
    print("Resolved image path:", image_path)
    print("File exists:", os.path.exists(image_path))
    print("File size:", os.path.getsize(image_path))
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Summary image not found")

    return FileResponse(image_path, media_type="image/png")


@router.get("/countries/{name}")
async def get_country_by_name(name: str, db: AsyncSession = Depends(get_session)):

    try:
        query = select(Country).where(Country.name == name)
        result = await db.execute(query)
        country = result.scalars().first()

        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Country not found"
                }
            )

        return country
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Country not found"
            }
        )


@router.delete("/countries/{name}")
async def delete_country_by_name(name: str, db: AsyncSession = Depends(get_session)):
    """ Delete country by name """
    query = select(Country).where(Country.name == name)
    result = await db.execute(query)
    
    country = result.scalars().first()

    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country {name} not found"
        )
    
    await db.delete(country)
    await db.commit()

    return None


@router.get("/status")
async def get_status(db: AsyncSession = Depends(get_session)):
    """
    Returns total countries and last refresh timestamp
    """
    try:
        query = await db.execute(select(func.count(Country.id)))
        total_countries = query.scalar_one()

        """ Get the latest refresh timestamps """
        last_refresh_query = await db.execute(
            select(func.max(Country.last_refreshed_at))
        )
        last_refresh = last_refresh_query.scalar_one()

        return {
            "total_countries": total_countries,
            "last_refreshed_at": last_refresh
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error fetching status {str(e)}" 
        )

