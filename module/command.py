try:
    from module import config
except:
    import config

list_of_command = ['kcag add anime',
                   'kcag add character',
                   'kcag remove anime',
                   'kcag remove character',
                   'kcag list anime',
                   'kcag list character',
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

            elif parameters[0] == 'character':
                parameters.pop(0)
                for character in parameters:
                    config.modify_file('character-list.txt', 'write', character)

        elif parameters[0] == 'remove':
            parameters.pop(0)
            if parameters[0] == 'anime':
                parameters.pop(0)
                for anime in parameters:
                    config.modify_file('anime-list.txt', 'remove', anime)

            elif parameters[0] == 'character':
                parameters.pop(0)
                for character in parameters:
                    config.modify_file('character-list.txt', 'remove', character)

        elif parameters[0] == 'list':
            parameters.pop(0)
            if parameters[0] == 'anime':
                file_content = config.modify_file('anime-list.txt', 'list')
                return file_content

            elif parameters[0] == 'character':
                file_content = config.modify_file('character-list.txt', 'list')
                return file_content

        elif parameters[0] == 'help':
            return list_of_command