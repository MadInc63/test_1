import os
import ast
import asyncio
import argparse
import configparser
from contextlib import suppress
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


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


def get_path_to_file():
    if os.path.exists('config.ini'):
        config = configparser.ConfigParser()
        config.read('config.ini')
        try:
            file_path = config['DEFAULT']['file_path']
        except KeyError:
            print('Bad config file')
            args = parse_args()
            file_path = args.file_path
    else:
        args_list = parse_args()
        file_path = args_list.file_path
    return os.path.abspath(file_path)


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


async def async_handler(file):
    with open(file, 'r') as log_file:
        for line in log_file:
            line = line.strip()
            with suppress(ValueError, SyntaxError):
                array = ast.literal_eval(line)
            if isinstance(array, (list, tuple)):
                tab_count = 1
                print('Массив')
                await read_array(array, tab_count)
            elif isinstance(line, (int, float)):
                print('Число {digit}'.format(digit=line))
            else:
                print('Строка {string}'.format(string=line))


class CustomHandler(PatternMatchingEventHandler):
    def __init__(self, loop, *args, **kwargs):
        self._loop = loop
        super().__init__(*args, **kwargs)

    def on_modified(self, event):
        if not event.is_directory:
            asyncio.run_coroutine_threadsafe(
                async_handler(event.src_path),
                self._loop
            )


if __name__ == "__main__":
    path_to_file = get_path_to_file()
    base_path_to_file, file_name = os.path.split(path_to_file)
    async_loop = asyncio.get_event_loop()
    event_handler = CustomHandler(async_loop)
    event_handler._patterns = ['*/{file_name}'.format(file_name=file_name)]
    observer = Observer()
    observer.schedule(event_handler, base_path_to_file, recursive=False)
    observer.start()
    try:
        async_loop.run_forever()
    except KeyboardInterrupt:
        observer.stop()
        for task in asyncio.Task.all_tasks():
            task.cancel()
            with suppress(asyncio.CancelledError):
                async_loop.run_until_complete(task)
    finally:
        async_loop.close()
        observer.join()
