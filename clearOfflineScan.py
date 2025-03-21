import os
import glob

def delete_files_with_suffix(directory, suffix):
    # 使用 glob 模块找到所有具有特定后缀的文件
    files = glob.glob(directory + '/**/*' + suffix, recursive=True)
    for file in files:
        try:
            os.remove(file)  # 删除文件
            print(f"File {file} has been deleted.")
        except OSError as e:
            print(f"Error: {file} : {e.strerror}")

def delete_file_if_exists(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)
        print(f"File {filepath} has been deleted.")
    else:
        print(f"File {filepath} does not exist.")

# prompt user to confirm yes or no before deleting
def confirm_delete(prompt):
    while True:
        answer = input(prompt)
        if answer == 'y':
            delete_files_with_suffix('./static/feature', '.npy')
            delete_file_if_exists('static/npyToFilePath.json')
        elif answer == 'n':
            return False
        else:
            print("Please enter y or n.")

confirm_delete("Are you sure you want to delete all scan cached files? (y/n) ")
