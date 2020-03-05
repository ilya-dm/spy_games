import requests
import time
from datetime import datetime
import json

access_token = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'
ID = 171691064
sleep_time = 0.3


class User:
    def __init__(self, id):
        self.token = access_token
        self.id = id
        self.link = 'https://vk.com/id' + str(self.id)

    def get_mutual_friends(self, user_id, target_id):
        self.user_id = user_id
        self.target_id = target_id
        mutual_friends = []
        first_user = requests.get('https://api.vk.com/method/users.get',
                                  params={'access_token': access_token, 'user_id': user_id, 'v': '5.52',
                                          'fields': ['first_name', 'last_name']}).json()['response']
        name_surname_1 = first_user[0]['first_name'] + ' ' + first_user[0]['last_name']

        second_user = requests.get('https://api.vk.com/method/users.get',
                                   params={'access_token': access_token, 'user_id': target_id, 'v': '5.52',
                                           'fields': ['first_name', 'last_name']}).json()['response']
        name_surname_2 = second_user[0]['first_name'] + ' ' + second_user[0]['last_name']

        params = {'access_token': access_token,
                  'source_uid': user_id,
                  'target_uid': self.target_id,
                  'v': '5.52'}
        response = requests.get('https://api.vk.com/method/friends.getMutual', params=params)
        for ID in response.json()['response']:
            response_params = {'access_token': access_token,
                               'user_id': ID,
                               'v': '5.52',
                               'fields': ['first_name', 'last_name']}
            friend = requests.get('https://api.vk.com/method/users.get', params=response_params)
            mutual_friends.append(friend.json())
            time.sleep(0.3)
            print('running...')
        print(f'Общие друзья: у {name_surname_1} и {name_surname_2}:')
        for data in mutual_friends:
            resp = data['response'][0]
            first_name = resp['first_name']
            last_name = resp['last_name']
            ID = str(resp['id'])
            link = 'https://vk.com/id' + ID
            print(f'{first_name} {last_name}: {link}')

    def get_friends(self):
        friend_list = list()
        params = {'access_token': access_token, 'user_ids': self.id, 'v': '5.52',
                  'fields': ['first_name', 'last_name']}
        response = requests.get('https://api.vk.com/method/friends.get', params=params)
        friends = response.json().get('response')
        print(friends)
        for element in friends['items']:
            friend_list.append({'id': element['id'], 'first_name': element['first_name'],
                                'last_name': element['last_name']})
        return friend_list

    def get_groups(self, user_id):
        group_list = list()
        group_set = set()
        params = {'access_token': access_token, 'user_id': user_id, 'v': '5.52',
                  'extended': 1, 'fields': ['members_count']}
        response = requests.get('https://api.vk.com/method/groups.get', params=params).json()
        resp = response.get('response')
        if resp is not None:
            items = resp.get('items')
            for item in items:
                try:
                    description = {'gid': item['id'], 'name': item['name'], 'members_count': item['members_count']}
                    group_list.append(description)
                    group_set.add(item['id'])
                except KeyError:
                    continue

        return group_list, group_set


user = User(ID)

self_groups, groups_set = user.get_groups(ID)
friends_list = user.get_friends()
start = datetime.now()
counter = 0
friends_groups = set()
json_list = list()

for index in range(0, len(friends_list)):
    print(f'Осталось обработать {len(friends_list) - counter} друзей')
    counter += 1
    friends_groups.update(user.get_groups(friends_list[index]['id'])[1])
    time.sleep(sleep_time)
groups = groups_set.difference(friends_groups)
finish = datetime.now()
for group in self_groups:
    if group['gid'] in groups_set:
        json_list.append(group)
print(json_list)
with open("groups.json", "w") as f:
    f.write(json.dumps(json_list, ensure_ascii=False))
print(f'Время исполнения составило {finish - start}')
