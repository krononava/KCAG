from module import config

list_of_command = ['kcag add anime',
                   'kcag remove anime',
                   'kcag list anime',
                   'kcag help']

def parser(message: str):
    parameters = message.split(' ')

    if parameters[0] == 'kcag':
        parameters.pop(0)

        if parameters[0] == 'add':
            parameters.pop(0)
            if parameters[0] == 'anime':
                parameters.pop(0)
                for anime in parameters:
                    config.modify_file('anime-list.txt', 'write', anime)

        elif parameters[0] == 'remove':
            parameters.pop(0)
            if parameters[0] == 'anime':
                parameters.pop(0)
                for anime in parameters:
                    config.modify_file('anime-list.txt', 'remove', anime)

        elif parameters[0] == 'list':
            parameters.pop(0)
            if parameters[0] == 'anime':
                file_content = config.modify_file('anime-list.txt', 'list')
                return file_content

        elif parameters[0] == 'help':
            return list_of_command