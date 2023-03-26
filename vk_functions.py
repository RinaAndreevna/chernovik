import vk_api
import json
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_config import group_token, user_token, V
from vk_api.exceptions import ApiError
from models import engine, Base, Session, User, DatingUser, Photos, BlackList
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from SQL_func import insert_user


token = input('Token: ')

# Для работы с ВК
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk)
# Для работы с БД
session = Session()
connection = engine.connect()

""" 
ФУНКЦИИ ПОИСКА
"""
# Ищет людей по критериям
def search_users(session, user_id):
    search_data = vk.users.get(user_ids=user_id, fields='sex, home_town, bdate')
    user_age = int(search_data[0]['bdate'][-4:])
    user_name = f"{search_data[0]['first_name']} {search_data[0]['last_name']}"
    user_city = search_data[0]['home_town']
    insert_user(session=session, vk_id=str(user_id), name=user_name, age=user_age, city=user_city, sex=search_data[0]['sex'])
    inquiry = vk.users.search(age_from=(datetime.datetime.now().year-5)-user_age, age_to=(datetime.datetime.now().year+5)-user_age, hometown=search_data[0]['home_town'], sex=3-search_data[0]['sex'], has_photo=1, count=25, is_closed=False, can_access_closed=True, deactivated=None)
    candidates = []

    for item in inquiry['items']:
        candidate = {key: value for (key, value) in item.items() if
                     key in ['id', 'first_name', 'last_name'] and not item['is_closed']}

        if candidate:
            candidates.append(candidate)
        else:
            continue

    result = f'Советуем посмотреть на кандидатов:\n{candidates[0]["first_name"]} {candidates[0]["last_name"]}' \
             f'\nid во Вконтакте: {candidates[0]["id"]}\n{candidates[1]["first_name"]} {candidates[1]["last_name"]}' \
             f'\nid во Вконтакте: {candidates[1]["id"]}'

    return result, candidates
    # return True


# Находит фото людей
def get_photo(user_owner_id):
    vk_ = vk_api.VkApi(token=user_token)
    try:
        response = vk_.method('photos.get',
                              {
                                  'access_token': user_token,
                                  'v': V,
                                  'owner_id': user_owner_id,
                                  'album_id': 'profile',
                                  'count': 10,
                                  'extended': 1,
                                  'photo_sizes': 1,
                              })
    except ApiError:
        return 'нет доступа к фото'
    users_photos = []
    for i in range(10):
        try:
            users_photos.append(
                [response['items'][i]['likes']['count'],
                 'photo' + str(response['items'][i]['owner_id']) + '_' + str(response['items'][i]['id'])])
        except IndexError:
            users_photos.append(['нет фото.'])
    return users_photos
    # return True


""" 
ФУНКЦИИ СОРТИРОВКИ, ОТВЕТА, JSON
"""


# Сортируем фото по лайкам, удаляем лишние элементы
def sort_likes(photos):
    result = []
    for element in photos:
        if element != ['нет фото.'] and photos != 'нет доступа к фото':
            result.append(element)
    return sorted(result)


#  JSON file create with result of programm
def json_create(lst):
    today = datetime.date.today()
    today_str = f'{today.day}.{today.month}.{today.year}'
    res = {}
    res_list = []
    for num, info in enumerate(lst):
        res['data'] = today_str
        res['first_name'] = info[0]
        res['second_name'] = info[1]
        res['link'] = info[2]
        res['id'] = info[3]
        res_list.append(res.copy())

    with open("result.json", "a", encoding='UTF-8') as write_file:
        json.dump(res_list, write_file, ensure_ascii=False)

    print(f'Информация о загруженных файлах успешно записана в json файл.')
