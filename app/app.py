import random
import re

from faker import Faker
from flask import Flask, make_response, redirect, render_template, request, url_for

fake = Faker()

app = Flask(__name__)
application = app

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']

PHONE_INVALID_DIGITS_COUNT = 'Недопустимый ввод. Неверное количество цифр.'
PHONE_INVALID_SYMBOLS = 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'


def generate_comments(replies=True):
    comments = []
    for i in range(random.randint(1, 3)):
        comment = {'author': fake.name(), 'text': fake.text()}
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments


def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }


def validate_and_format_phone(phone):
    if not re.fullmatch(r'[0-9\s().+\-]*', phone):
        return None, PHONE_INVALID_SYMBOLS

    digits = ''.join(symbol for symbol in phone if symbol.isdigit())
    phone_without_spaces = phone.strip()

    if phone_without_spaces.startswith('+7') or phone_without_spaces.startswith('8'):
        required_digits_count = 11
    else:
        required_digits_count = 10

    if len(digits) != required_digits_count:
        return None, PHONE_INVALID_DIGITS_COUNT

    if required_digits_count == 11:
        digits = digits[1:]

    formatted_phone = f'8-{digits[0:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:10]}'
    return formatted_phone, None


posts_list = sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)


@app.route('/')
def index():
    return render_template('index.html', title='Лабораторная работа №2')


@app.route('/request/args')
def request_args():
    return render_template(
        'request_data.html',
        title='Параметры URL',
        heading='Параметры URL',
        description='На странице отображаются параметры, переданные в адресной строке после знака вопроса.',
        data=request.args.items(multi=True),
        empty_message='Параметры URL не переданы. Для проверки добавьте их в адресную строку, например: ?name=Alex&group=241-3211.'
    )


@app.route('/request/headers')
def request_headers():
    return render_template(
        'request_data.html',
        title='Заголовки запроса',
        heading='Заголовки запроса',
        description='На странице отображаются HTTP-заголовки текущего запроса.',
        data=request.headers.items(),
        empty_message='Заголовки запроса отсутствуют.'
    )


@app.route('/request/cookies')
def request_cookies():
    return render_template(
        'request_data.html',
        title='Cookie',
        heading='Cookie',
        description='На странице отображаются cookie, переданные браузером в текущем запросе.',
        data=request.cookies.items(),
        empty_message='Cookie не найдены. Можно установить тестовые cookie для проверки.',
        show_cookie_button=True
    )


@app.route('/request/cookies/set')
def set_demo_cookies():
    response = make_response(redirect(url_for('request_cookies')))
    response.set_cookie('student', 'Klevin_Alexandr')
    response.set_cookie('group', '241-3211')
    return response


@app.route('/request/form', methods=['GET', 'POST'])
def request_form():
    form_data = request.form.items() if request.method == 'POST' else []
    return render_template(
        'login_form.html',
        title='Форма авторизации',
        form_data=form_data,
        was_submitted=request.method == 'POST'
    )


@app.route('/phone', methods=['GET', 'POST'])
def phone():
    phone_value = ''
    formatted_phone = None
    error = None

    if request.method == 'POST':
        phone_value = request.form.get('phone', '')
        formatted_phone, error = validate_and_format_phone(phone_value)

    return render_template(
        'phone.html',
        title='Проверка телефона',
        phone=phone_value,
        formatted_phone=formatted_phone,
        error=error
    )


@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list)


@app.route('/posts/<int:index>')
def post(index):
    p = posts_list[index]
    return render_template('post.html', title=p['title'], post=p)


@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')


if __name__ == '__main__':
    app.run(debug=True)
