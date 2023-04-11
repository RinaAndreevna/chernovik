import vk_api
from random import randrange
from vk_api.keyboard import VkKeyboard
from vk_api.bot_longpoll import VkBotLongPoll
from config import group_id


class Legacy: # Реализация бота в виде класса
	def __init__(self, group_token):
		self.token = group_token
		self.vk = vk_api.VkApi(token=group_token)
		self.longpoll = VkBotLongPoll(vk=self.vk, group_id=group_id)
		self.vk_api = self.vk.get_api()

	def create_keyboard(self, buttons=[], one_time=True, inline=False):
		keyboard = VkKeyboard(one_time=one_time, inline=inline)
		count = 0
		for button in buttons:
			if button['type'] == 'text':
				if count > 2:
					keyboard.add_line()
					count = 0
				name = button['name']
				color = button['color']
				keyboard.add_button(label=f'{name}', color=color)
				count += 1
			elif button['type'] == 'link':
				if count > 2:
					keyboard.add_line()
					count = 0
				name = button['name']
				link = button['link']
				keyboard.add_openlink_button(label=f'{name}', link=link)
				count += 1
			elif button['type'] == 'location':
				keyboard.add_location_button(payload='{"button": "send_location"}')
		return keyboard

	def get_name(self, user_id):
		name = []
		name.append(self.vk.method('users.get', {'user_ids': user_id, 'name_case': 'nom'})[0]['first_name'])
		name.append(self.vk.method('users.get', {'user_ids': user_id, 'name_case': 'nom'})[0]['last_name'])
		return name

	def write_msg(self, user_id, message, keyboard=None):
		self.vk.method('messages.send',
					   {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), 'keyboard': keyboard})

	def send_photo(self, user_id, attachment=None, keyboard=None):
		if len(attachment) == 0:
			self.vk.method('messages.send', {'user_id': user_id, 'message': 'У пользователя нельзя получить фото',
											 'random_id': randrange(10 ** 7), 'keyboard': keyboard})
		else:
			length = len(attachment)
			self.vk.method('messages.send', {'user_id': user_id, 'message': 'у пользователя {} фото'.format(length),
											 'random_id': randrange(10 ** 7)})
			self.vk.method('messages.send',
						   {'user_id': user_id, 'attachment': ','.join(attachment), 'random_id': randrange(10 ** 7),
							'keyboard': keyboard})
