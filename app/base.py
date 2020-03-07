import aiohttp
from bs4 import BeautifulSoup
import asyncio


class Base:
    """
    base class for package
    all dirty works will be done here.
    """

    # send request to subscene and get the response
    async def request(self, session: aiohttp.ClientSession, url: str):
        resp = await session.request('GET', url=url)
        if resp.status != 200:
            await asyncio.sleep(3)
            resp = await session.request('GET', url=url)
        return await resp.text()

    async def aiorequest(self, url):
        costume_headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                                '(KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
        async with aiohttp.ClientSession(headers=costume_headers) as session:
            html = await self.request(session, url)
            return html