from bs4 import BeautifulSoup
from .base import Base
import re


class Subscene(Base):
    async def search(self, title):
        """
        search function gives a title and search for it in subscene
        results will be passed as list of dicts, sample:
        {"name": "movie/series title", "link": "link to that title", "count": "counts"}
        """
        try:
            url = f"https://subscene.com/subtitles/searchbytitle?query={title}"
            resp = await self.aiorequest(url=url)  # send request to Subscene
            if " " in title:
                title = title.replace(" ", "+")
            soup = BeautifulSoup(resp, 'lxml')
            find_ul = soup.find('div', class_='search-result').find_all('ul')  # .find('ul')

            subtitles = []  # list for all finded subs to return
            for ul in find_ul:
                find_li = ul.find_all('li')
                for li in find_li:
                    base_li = li.find('div', class_='title').a
                    name = base_li.text  # movie/show name
                    link = base_li['href']  # movie/show url
                    try:  # movie/show subtitle counts
                        sub_count = li.find('div', class_='subtle count').text
                    except:
                        sub_count = li.find('span', class_='subtle count').text
                    sub_count = re.findall(r'\d+', sub_count)[0]

                    link = "https://subscene.com" + link

                    data = {"name": name, "link": link, "count": int(sub_count)}
                    subtitles.append(data)

            return subtitles
        except Exception as e:
            print(e)
            return []

    async def subtitles(self, url, lang=None):
        try:
            resp = await self.aiorequest(url, lang)
            soup = BeautifulSoup(resp, 'lxml')
            title = soup.find('div', class_='box clearfix').find('div', class_='top left').find('div',
                                                                                                class_='header').h2.text
            try:
                title = title.replace("Flag", "")
                title = title.replace("Imdb", "").strip()
            except:
                pass

            table = soup.table.tbody.find_all('tr')

            subtitles = []
            for tr in table:
                try:
                    sub_name = tr.find('td', class_='a1').a.find_all('span')[1].text.strip()  # release title
                except AttributeError:
                    continue
                sub_link = tr.find('td', class_='a1').a['href']  # release link
                try:
                    sub_owner = tr.find('td', class_='a5').a.text.strip()  # sub owner
                except:
                    sub_owner = "Anonymous"
                try:
                    comments = tr.find('td', class_='a6').text.strip()
                except:
                    comments = ""
                sub_link = "https://subscene.com" + sub_link

                sub = {"name": sub_name, "link": sub_link, "owner": sub_owner, "comments": comments}
                subtitles.append(sub)

            re_subtitles = {"title": title, "subtitles": subtitles}
            return re_subtitles
        except Exception as e:
            print(e)
            return []

    async def down_page(self, url):
        resp = await self.aiorequest(url)
        soup = BeautifulSoup(resp, 'lxml')

        maindiv = soup.body.find('div', class_='subtitle').find('div', class_='top left')
        title = maindiv.find('div', class_='header').h1.span.text.strip()
        try:
            imdb = maindiv.find('div', class_='header').h1.a['href']
        except TypeError:
            imdb = ""
        try:
            poster = maindiv.find('div', class_='poster').a['href']
        except:
            poster = ""
        try:
            author_name = maindiv.find('div', class_='header').ul.find('li', class_='author').a.text.strip()
            author_link = f"https://subscene.com{maindiv.find('div', class_='header').ul.find('li', class_='author').a['href']}"
        except:
            author_link = ""
            author_name = "Anonymous"

        download_url = f"https://subscene.com{maindiv.find('div', class_='header').ul.find('li', class_='clearfix').find('div', class_='download').a['href']}"

        try:
            comments = maindiv.find('div', class_='header').ul.find('li', class_='comment-wrapper').find('div',
                                                                                                         class_='comment').text
        except:
            comments = ""
        try:
            release = maindiv.find('div', class_='header').ul.find('li', class_='release').find_all('div')
            releases = ""
            for i in range(2):
                r = release[i].text.strip()
                releases = releases + f"\n{r}"
        except Exception as e:
            releases = ""

        response = {"title": title, "imdb": imdb, "poster": poster, "author_name": author_name,
                    "author_url": author_link, "download_url": download_url, "comments": comments, "releases": releases}
        return response

    async def download(self, url, file_path):
        resp = await self.download_file(url, file_path)

        return resp