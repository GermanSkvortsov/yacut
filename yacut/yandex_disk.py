"""Модуль для асинхронной работы с API Яндекс Диска."""

import asyncio
import urllib.parse

import aiohttp


class YandexDisk:
    """Класс для асинхронной загрузки файлов на Яндекс Диск."""

    def __init__(self, token):
        """Инициализация с токеном доступа к Яндекс Диску."""
        self.token = token
        self.api_host = 'https://cloud-api.yandex.net/'
        self.api_version = 'v1'

    async def _get_upload_url(self, session, filename):
        """Получение временной ссылки для загрузки файла."""
        url = (
            f'{self.api_host}{self.api_version}'
            f'/disk/resources/upload'
        )
        headers = {'Authorization': f'OAuth {self.token}'}
        params = {'path': f'app:/{filename}', 'overwrite': 'True'}
        async with session.get(
            url, headers=headers, params=params
        ) as response:
            data = await response.json()
            if 'href' not in data:
                raise Exception(
                    f'Ошибка получения URL для загрузки: {data}'
                )
            return data['href']

    async def _upload_file_to_disk(self, session, file_obj, filename):
        """Загрузка одного файла на Яндекс Диск и получение ссылки."""
        upload_url = await self._get_upload_url(session, filename)

        if hasattr(file_obj, 'read'):
            file_data = file_obj.read()
        elif hasattr(file_obj, 'getvalue'):
            file_data = file_obj.getvalue()
        else:
            file_data = file_obj

        headers = {'Authorization': f'OAuth {self.token}'}
        async with session.put(upload_url, data=file_data) as response:
            if response.status not in (200, 201, 202):
                raise Exception(
                    f'Ошибка загрузки файла: {response.status}'
                )
            location = response.headers.get('Location', '')
            location = urllib.parse.unquote(location)
            location = location.replace('/disk', '')

        download_url = (
            f'{self.api_host}{self.api_version}'
            f'/disk/resources/download'
        )
        async with session.get(
            download_url, headers=headers, params={'path': location}
        ) as response:
            data = await response.json()
            if 'href' not in data:
                raise Exception(
                    f'Ошибка получения ссылки на скачивание: {data}'
                )
            return data['href']

    async def upload_files(self, files):
        """Загрузка нескольких файлов параллельно и получение ссылок."""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._upload_file_to_disk(session, file, file.filename)
                for file in files
            ]
            urls = await asyncio.gather(*tasks)
        return urls
