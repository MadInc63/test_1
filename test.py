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
        default='file.log'
    )
    return parser.parse_args()


async def read_file_by_line(log_file):
    while True:
        data = log_file.readline().strip()
        if data:
            return data
        await asyncio.sleep(0.1)


async def read_array(array, tab_count):
    for item in array:
        if isinstance(item, (list, tuple)):
            print('\t' * tab_count + 'Массив')
            tab_count += 1
            await read_array(item, tab_count)
            tab_count -= 1
        elif isinstance(item, (int, float)):
            print('\t' * tab_count + 'Число - {digit}'.format(digit=item))
        else:
            print('\t' * tab_count + 'Строка - {string}'.format(string=item))
        await asyncio.sleep(0.1)


async def read_file(path):
    with open(path, 'r', encoding='utf-8') as log_file:
        log_file.seek(0, 2)
        while True:
            line = await read_file_by_line(log_file)
            try:
                array = ast.literal_eval(line)
            except ValueError:
                array = None
            # except SyntaxError:
            #     array = None
            if isinstance(array, (list, tuple)):
                tab_count = 1
                print('Массив')
                await read_array(array, tab_count)
            elif isinstance(line, (int, float)):
                print('Число {digit}'.format(digit=line))
            else:
                print('Строка {string}'.format(string=line))
            await  asyncio.sleep(0.1)


if __name__ == '__main__':
    args = parse_args()
    file_path = args.file_path
    config = configparser.ConfigParser()
    config.read('config.ini')
    try:
        log_file_path = config['DEFAULT']['file_path']
    except KeyError:
        pass
    loop = asyncio.get_event_loop()
    loop.run_until_complete(read_file(file_path))
