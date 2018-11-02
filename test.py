import ast
import asyncio
import argparse
import configparser


def parse_args():
    parser = argparse.ArgumentParser(description='Log parser')
    parser.add_argument(
        'file_path',
        type=str,
        help='read file path',
        nargs='?',
        default='log.txt'
    )
    return parser.parse_args()


async def read_file_by_line(log_file):
    while True:
        data = log_file.readline().strip()
        if data:
            return data
        await asyncio.sleep(0.5)


async def read_array(array, tab_count):
    for item in array:
        if isinstance(item, (list, tuple)):
            print('\t' * tab_count + 'Массив')
            tab_count += 1
            await read_array(item, tab_count)
            tab_count -= 1
        else:
            if isinstance(item, (int, float)):
                print('\t' * tab_count + 'Число - {digit}'.format(digit=item))
            elif isinstance(item, str):
                print(
                    '\t' * tab_count + 'Строка - {string}'.format(string=item)
                )
    await asyncio.sleep(0.1)


async def find(file_path):
    with open(file_path, 'r') as log_file:
        while True:
            line = await read_file_by_line(log_file)
            line = ast.literal_eval(line)
            if isinstance(line, (int, float)):
                print('Число - {digit}'.format(digit=line))
            elif isinstance(line, str):
                print('Строка - {string}'.format(string=line.strip()))
            elif isinstance(line, (list, tuple)):
                print('Массив')
                tab_count = 1
                await read_array(line, tab_count)


if __name__ == '__main__':
    args = parse_args()
    log_file_path = args.file_path
    config = configparser.ConfigParser()
    config.read('config.ini')
    try:
        log_file_path = config['DEFAULT']['file_path']
    except KeyError:
        pass
    loop = asyncio.get_event_loop()
    loop.run_until_complete(find(log_file_path))
