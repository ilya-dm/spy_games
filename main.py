import requests
import time
import json


class User:
    def __init__(self, id):

        self.id = id

    def get_friends(self):
        friend_list = list()
        params = {'access_token': access_token, 'user_id': self.resolveScreenName(self.id), 'v': V,
                  'fields': ['first_name', 'last_name']}
        response = requests.get(f'{API}/friends.get', params=params)
        friends = response.json().get('response')
        for element in friends['items']:
            friend_list.append(str(element['id']))
        return friend_list

    def get_groups(self):
        group_list = list()
        group_set = set()
        params = {'access_token': access_token, 'user_id': self.resolveScreenName(self.id), 'v': '5.52',
                  'extended': 1, 'fields': ['members_count']}
        response = requests.get(f'{API}/groups.get', params=params).json()
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

    def resolveScreenName(self, screen_name):
        params = {'access_token': access_token, 'screen_name': screen_name, 'v': '5.52'}
        response = requests.get(f"{API}/utils.resolveScreenName", params=params).json()['response']
        ID = response['object_id']
        return ID

    def get_groups_by_execute(self):
        friends_list = self.get_friends()
        offset = 25
        counter = 1
        in_progress = 0
        items_set = set()
        for index in range(0, len(friends_list), offset):
            list_to_execute = friends_list[offset * (counter - 1):offset * counter]
            a = f"{','.join(list_to_execute)}"
            code = '''var a = Args.a.split(',');
                      var i = 0;
                      var c = [];
                      while (i <25)
                      {
                          var groups = API.groups.get({'user_id':a[i]});
                          c.push(groups);
                          i= i+ 1;
                      }
                      return c;'''
            params = {'access_token': access_token, 'code': code, 'a': a, 'v': V}
            response = requests.get(url=f'{API}/execute', params=params)
            counter += 1
            print(f'Осталось обработать {len(friends_list) - in_progress} друзей')
            in_progress += offset
            time.sleep(0.3)
            resp = response.json()['response']
            for user_groups in resp:
                if type(user_groups) == dict:
                    a = user_groups.get('items')
                    items_set.update(a)
        return items_set


def get_unique_groups():
    user = User(user_id)
    friends_groups = user.get_groups_by_execute()
    mutual_groups = set()
    group_set = user.get_groups()[1]
    unique_groups = group_set.difference(friends_groups)
    groups_with_friends = group_set.intersection(friends_groups)
    for group in groups_with_friends:
        params = {'access_token': access_token, 'group_id': group, 'filter': 'friends', 'v': V}
        response = requests.get(url=f'{API}/groups.getMembers', params=params)
        resp = response.json()['response']
        if resp['count'] <= n:
            mutual_groups.add(group)
        print('Группы с общими друзьями обрабатываются...')
        time.sleep(0.3)
    return unique_groups, mutual_groups


def write_json():
    user = User(user_id)
    unique_groups = list()
    mutual_groups = list()
    json_dict =dict()
    groups, groups_with_friends = get_unique_groups()
    self_groups = user.get_groups()[0]
    for group in self_groups:
        if group['gid'] in groups:
            unique_groups.append(group)
        if group['gid'] in groups_with_friends:
            mutual_groups.append(group)
        json_dict[f'Уникальные группы пользователя {user_id}:'] = unique_groups
        json_dict[f'Группы, в которых есть не больше {n} друзей:'] = mutual_groups
    with open("groups.json", "w") as f:
        f.writelines(json.dumps(json_dict, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    API = "https://api.vk.com/method"
    V = "5.52"
    with open('token.txt', 'r') as f:
        access_token = f.read()
    user_id = input("Введите id в формате idXXXXX, или screen name пользователя: ")
    n = int(input("Введите максимальное количество друзей в группе: "))
    write_json()
