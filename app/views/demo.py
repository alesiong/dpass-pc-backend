import json
from werkzeug.datastructures import LanguageAccept
from werkzeug.http import parse_accept_header

from flask import Blueprint, render_template, request

bp = Blueprint('pages', __name__, url_prefix='/pages')


def get_locale():
    lang = request.args.get('lang', '')
    if lang == 'zh':
        return 'zh'
    elif lang == 'en':
        return 'en'
    user_agent = request.headers.get('User-Agent', '')
    accept_language = request.headers.get('Accept-Language', '')
    if 'zh' in user_agent:
        return 'zh'
    elif 'en' in user_agent:
        return 'en'
    accept = parse_accept_header(accept_language,
                                 LanguageAccept().best_match(['zh', 'en']))
    if accept and 'zh' in accept[0][0]:
        return 'zh'
    return 'en'


def get_locale_with_translation_and_args():
    locale = get_locale()
    tr = get_translation()[locale]
    args = {k: v for k, v in request.args.items()}
    args['lang'] = tr['other_lang']
    return locale, tr, args


def get_translation():
    translation = {'zh': {}, 'en': {}}
    with open('resources/translation.csv', encoding='utf-8') as f:
        f.readline()
        for l in f:
            l = l.replace('\\,', '%2C')
            l = l.replace('\n', '')
            l = l.replace('\r', '')
            l = l.replace('\\n', '\n')
            key, zh, en = l.split(',')[:3]
            translation['zh'][key] = zh.replace('%2C', ',')
            translation['en'][key] = en.replace('%2C', ',')
    return translation


def get_resource(name, locale):
    return json.load(open('resources/%s/%s.json' % (locale, name), encoding='utf-8'))


@bp.route('/demo/')
def demo():
    locale, tr, args = get_locale_with_translation_and_args()
    shuttle_info = get_resource('shuttle', locale)
    notice = get_resource('shuttle_notice', locale)
    return render_template('page/demo.html',
                           tr=tr,
                           data=shuttle_info,
                           notice=notice,
                           url='pages.demo',
                           args=args)
