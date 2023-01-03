import vk_api
import time

vk = vk_api.VkApi(token='community token')
long_poll = vk.method('messages.getLongPollServer', {'need_pts': 1})
server, key, pts = long_poll['server'], long_poll['key'], long_poll['pts']

while True:
    long_poll = vk.method('messages.getLongPollHistory', {
        'pts': pts,
        'preview_length': 0,
        'history_length': 1,
        'onlines': 1,
        'fields': 'city,relation,sex,age',
        'events_limit': 1000,
        'server': server,
        'key': key
    })
    updates = long_poll['updates']
    for update in updates:
        if update[0] == 4:
            user_id = update[3]
            body = update[5]
            if body[0] == '/':
                cmd, *args = body[1:].split()
                if cmd == 'начать':
                    vk.method('messages.send', {
                        'peer_id': user_id,
                        'message': 'Привет! Как я могу тебе помочь?'
                    })
                elif cmd == 'поиск':
                    gender = None
                    age = None
                    city = None
                    relation = None
                    user_info = vk.method('users.get', {'user_ids': user_id})[0]
#                     if 'sex' in user_info:
#                         gender = 'мужской' if user_info['sex'] == 2 else 'женский'
                    gender = None
                    if 'age' in user_info:
                        age = user_info['age']
                    if 'city' in user_info:
                        city = user_info['city']['id']
                    if 'relation' in user_info:
                        relation = user_info['relation']
                    if not gender:
                        vk.method('messages.send', {
                            'peer_id': user_id,
                            'message': 'Какого пола ты ищешь? Введи "мужской" или "женский".'
                        })
                        continue
                    if not age:
                        vk.method('messages.send', {
                            'peer_id': user_id,
                            'message': 'Какого возраста ты ищешь?'
                        })
                        continue
                    if not city:
                        vk.method('messages.send', {
                           
                            'peer_id': user_id,
                            'message': 'В каком городе ты ищешь?'
                        })
                        continue
                    params = {'count': 10, 'fields': 'city,relation'}
                    params['sex'] = 1 if gender == 'мужской' else 2
                    params['age_from'] = age
                    params['age_to'] = age
                    params['city'] = city
                    params['status'] = 6 if relation == 'замужем' else 1
                    response = vk.method('users.search', params)
                    vk.method('messages.send', {
                        'peer_id': user_id,
                        'message': response
                    })
    pts += len(updates)
    time.sleep(0.5)
