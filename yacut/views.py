"""Вьюхи приложения YaCut."""

import asyncio

from flask import flash, redirect, render_template, url_for

from . import app
from .constants import FILES_SHORT_ID
from .forms import FileForm, URLForm
from .models import ShortLinkCreationError, URLMap
from .yandex_disk import YandexDisk


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница: форма создания короткой ссылки."""
    form = URLForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    original = form.original_link.data
    custom_id = (form.custom_id.data or '').strip() or None

    try:
        url_map = URLMap.create(original, custom_id)
    except ShortLinkCreationError as error:
        flash(str(error))
        return render_template('index.html', form=form)

    data = url_map.to_dict()
    short_url = url_for(
        'redirect_to_url', short_id=data['short_link'], _external=True
    )
    return render_template(
        'index.html', form=form, short_url=short_url
    )


@app.route('/' + FILES_SHORT_ID, methods=['GET', 'POST'])
def files_view():
    """Страница загрузки файлов на Яндекс Диск."""
    form = FileForm()
    if not form.validate_on_submit():
        return render_template('files.html', form=form)

    disk = YandexDisk(app.config['DISK_TOKEN'])
    files = form.files.data
    download_urls = asyncio.run(disk.upload_files(files))
    results = []

    for file, download_url in zip(files, download_urls):
        try:
            url_map = URLMap.create(download_url)
        except ShortLinkCreationError:
            continue
        data = url_map.to_dict()
        results.append({
            'filename': file.filename,
            'short_url': url_for(
                'redirect_to_url', short_id=data['short_link'], _external=True
            )
        })

    return render_template('files.html', form=form, results=results)


@app.route('/<string:short_id>')
def redirect_to_url(short_id):
    """Переадресация на оригинальную ссылку по короткому идентификатору."""
    url_map = URLMap.get_by_short(short_id)
    if url_map is None:
        from flask import abort
        abort(404)
    return redirect(url_map.original)
