import os

config_files = os.listdir("config")

essential_files = ['account-token.txt', 'grab-channel.txt', 'spam-channel.txt']
optional_files = ['anime-list.txt', 'character-list.txt']
all_files = essential_files + optional_files

# Create config files if missing
def init_files() -> None:
    # this loop makes sure to create all missing files first
    for filename in all_files:
        file_path = 'config/' + filename
        if filename not in config_files:
            with open(file_path, 'a') as created_file:
                pass

    # this loop then verify the content of the created files
    for filename in all_files:
        file_path = 'config/' + filename
        with open(file_path, 'r') as existing_file:
            file_content = existing_file.read()
            if file_content == "" and filename in essential_files:
                raise EOFError(f"Missing {filename} configuration\nRefer to README.md documentation\n")

def modify_file(filename: str, modification: str, text: str = ""):
    parent_dir = os.path.abspath('..')
    file_path = 'config/' + filename
    with open(file_path, 'r+') as existing_file:
        file_content: list[str] = [line.strip() for line in existing_file.readlines()]
        if modification == 'write':
            file_content.append(text)
        elif modification == 'remove':
            file_content.remove(text)
        elif modification == 'list':
            return file_content
        existing_file.seek(0)
        existing_file.truncate()
        existing_file.writelines([line + "\n" for line in file_content])

        
if __name__ == "__main__":
    modify_file('anime-list.txt', 'list')