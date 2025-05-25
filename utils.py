from requests import request
from requests.exceptions import ConnectTimeout
from bs4 import BeautifulSoup


def get_request(lists_gosts: list[str]) -> list[tuple]:
    """Функция для отпрвки запроса к Институту стандартизации и получение данных об ГОСТ"""
    for gost in lists_gosts:
        result: list = []

        try:
            response = request("GET", f"https://nd.gostinfo.ru/doc.aspx?catalogid=gost&classid=-1&search={gost}")
        except ConnectTimeout:
            return result

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            data = soup.find("table", class_="typetable")
            cells, rows = [], []
            try:
                for cell in data.find_all(['td', 'th']):
                    cells.append(cell.get_text(strip=True))
                rows.append(cells)
            except AttributeError:
                result.append((gost, f"Отловили ошибку тип + {data} ГОСТ - {gost}"))
                return result

            for row in rows:
                line = row[5:-1]
                for i in range(0, len(line), 6):
                    result.append((*line[i:i + 3],))

            return result
        else:
            return result
