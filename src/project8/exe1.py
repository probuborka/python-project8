import argparse
import requests
import asyncio
import aiohttp
import aiofiles
import os
import time
from pathlib import Path

def check_path(path):
    """Проверка пути к папке."""
    if not path or not isinstance(path, str):
        raise ValueError("Путь должен быть непустой строкой")
    
    path = Path(path)
    
    if not path.exists():
        raise ValueError(f"Путь '{path}' не существует")

"""Синхронное скачивание"""
def synch_download_files(path, URL, count_files = 5):
    # Проверка входных параметров
    if count_files <= 0:
        raise ValueError("Количество файлов должно быть больше 0")
    
    check_path(path)
    
    if not URL or not isinstance(URL, str):
        raise ValueError("URL должен быть непустой строкой")

    for file_number in range(1, count_files + 1):
        try:
            print(f"Скачивание изображения {file_number}...")
            
            cont = requests.get(URL)

            filename = f"synch_{file_number}.jpg"
            filepath = os.path.join(path, filename)
            with open(f'{filepath}', 'wb') as f:
                f.write(cont.content)
            print(f"Изображение {file_number} сохранено")

        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Ошибка при скачивании файла {file_number}: {e}")
        except OSError as e:
            raise OSError(f"Ошибка при сохранении файла {file_number}: {e}")
        except Exception as e:
            raise Exception(f"Неожиданная ошибка при обработке файла {file_number}: {e}")

"""Асинхронное скачивание"""
async def async_download_files(path, URL, count_files=5):
    """Формирование задач и запуск"""
    # Проверка входных параметров
    if count_files <= 0:
        raise ValueError("Количество файлов должно быть больше 0")
    
    check_path(path)
    
    if not URL or not isinstance(URL, str):
        raise ValueError("URL должен быть непустой строкой")
    
    # HTTP-сессия для асинхронных запросов
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, count_files + 1):
            task = download_file(session, path, URL, i)
            tasks.append(task)

        # параллельный запуск задач
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                print(f"Ошибка: {result}")
        
async def download_file(session, path, URL, file_number):
    """Сохранение файла асинхронно"""
    try:
        print(f"Скачивание изображения {file_number}...")
        
        async with session.get(URL) as response:
            # Проверяем успешность запроса
            response.raise_for_status()
                      
            # Читаем содержимое файла
            content = await response.read()
            
            filename = f"asynch_{file_number}.jpg"
            filepath = os.path.join(path, filename)
            # Записываем файл
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(content)
            
            print(f"Изображение {file_number} сохранено")

    except aiohttp.ClientError as e:
        raise aiohttp.ClientError(f"Ошибка при скачивании файла {file_number}: {e}")
    except OSError as e:
        raise OSError(f"Ошибка при сохранении файла {file_number}: {e}")
    except Exception as e:
        raise Exception(f"Неожиданная ошибка при обработке файла {file_number}: {e}")
    
def main():
    """Точка входа."""
    parser = argparse.ArgumentParser(description='Анализ структуры файлов и папок')
    parser.add_argument('--path', type=str, required=True, 
                       help='Путь к папке ')
    
    parser.add_argument('--url', type=str, required=True, 
                       help='URL')


    args = parser.parse_args()

    # args.path = '/home/user/dev/images'
    # args.url = 'https://placebear.com/g/200/300'
    
    # Синхронное скачивание
    try: 
        start_time = time.time()
        synch_download_files(path=args.path, URL=args.url,  count_files=5)
        execution_time_1 = time.time() - start_time
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # Асинхронное скачивание
    try: 
        start_time = time.time()
        asyncio.run(async_download_files(args.path, args.url, count_files=5))
        execution_time_2 = time.time() - start_time
    except Exception as e:
        print(f"Ошибка: {e}")

    #
    print(f"Время выполнения синхронного скачивания: {execution_time_1}")
    print(f"Время выполнения асинхронного скачивания: {execution_time_2}")

if __name__ == '__main__':
    main()