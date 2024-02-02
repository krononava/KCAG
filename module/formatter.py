
def get_textblock(text):
    if type(text) == list:
        list_to_string = '\n'.join(text)
    string_to_block = '```\n' + list_to_string + '\n```'
    return string_to_block