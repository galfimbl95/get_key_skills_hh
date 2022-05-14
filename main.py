import time
import requests
from bs4 import BeautifulSoup


def create_search_url(search_phrase: str, city: int = 1) -> str:  # 1 Москва, 2 СПб
    return f'https://hh.ru/search/vacancy?area={city}&fromSearchLine=true&text={search_phrase}'


def get_links_to_vacancies(url: str) -> list: # с каждой страницы забирается не более 20 вакансий, т.к. hh.ru сначала отдает 20, а потом подгружается остальные через JS
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
    }
    response = requests.get(url, headers=headers)
    # print(response.text)
    soup = BeautifulSoup(response.text, "lxml")
    tag_a_vacancies = soup.find_all(attrs={'data-qa': "vacancy-serp__vacancy-title"}) # находит на странице элементы с тегом a в которых содержится ссылка на вакансию
    links = []
    for a in tag_a_vacancies:
        links.append(a.get('href'))
    next_page_button = soup.find(attrs={"data-qa": "pager-next"}) # пытаемся найти кнопку перехода следующую страницу поисковой выдачи
    if next_page_button is not None:
        next_page_link = 'https://hh.ru' + next_page_button.get('href')
        return links + get_links_to_vacancies(next_page_link) # уходим в рекурсию чтобы забрать ссылки со всех страниц поисковой выдачи
    else:
        return links


def get_skills(url: str) -> list:
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    list_span = soup.find_all('span', class_='bloko-tag__section bloko-tag__section_text', ) # найти элементы в которых указываются ключевые навыки
    list_skills = []
    for span in list_span:
        list_skills.append(span.text.lower())
    return list_skills


if __name__ == '__main__':
    phrase = input('Введите фразу для поиска вакансий\n')
    city = input('Введите город для поиска\n 1 - Москва\\Россия\n 2 - Санкт-Петербург\n')
    search_url = create_search_url(phrase, 1)
    links_to_vacancies = get_links_to_vacancies(search_url)
    global_arr_skills = []
    for link in links_to_vacancies:
        skills = get_skills(link)
        global_arr_skills += skills
        time.sleep(1)

    report = {}
    for skill in global_arr_skills:
        if skill in report:
            report[skill] += 1
        else:
            report[skill] = 1

    sorted_tuples = sorted(report.items(), key=lambda item: item[1], reverse=True)
    sorted_dict = {k: v for k, v in sorted_tuples}

    print(
        f"По запросу {phrase} было найдено и обработано объявлений: {len(links_to_vacancies)} \nДалее приведен список "
        f"ключевых навыков и в скольких объявлениях они требуются")
    for key in sorted_dict:
        print(key + ": " + str(sorted_dict[key]))
