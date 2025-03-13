import aiohttp
import os

async def search_movie(query: str):
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": os.getenv("TMDB_API_KEY"),
        "query": query,
        "language": "ru-RU"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
            if data.get("results"):
                movie = data["results"][0]
                return {
                    "title": movie["title"],
                    "overview": movie["overview"],
                    "release_date": movie["release_date"],
                    "poster_url": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                }
            return None