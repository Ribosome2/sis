from pathlib import Path

from pathlib import Path
from collections import defaultdict

def count_file_types(directory):
    file_types = defaultdict(int)
    for file in Path(directory).rglob('*'):
        if file.is_file():
            file_types[file.suffix] += 1
    return file_types

directory = './static/img/svn'  # 替换为你的目录
file_types = count_file_types(directory)

for file_type, count in file_types.items():
    print(f'{file_type}: {count}')