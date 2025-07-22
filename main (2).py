from flask import Flask, request, render_template
import mechanize
import json
import time
from datetime import datetime

app = Flask(__name__)

g_headers = {
    'Connection': 'keep-alive',
    'authority': 'mbasic.facebook.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'referer': 'www.google.com',
    'sec-ch-prefers-color-scheme': 'light',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101"',
    'sec-ch-ua-full-version-list': '" Not A;Brand";v="99.0.0.0", "Chromium";v="101.0.4951.40"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-ch-ua-platform-version': '"11.0.0"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
}

def load_cookies_from_json(json_cookies, cookies):
    cookies_data = json.loads(json_cookies)
    for key, value in cookies_data.items():
        cookie = mechanize.Cookie(
            version=0, name=key, value=value,
            port=None, port_specified=False,
            domain='facebook.com', domain_specified=True, domain_initial_dot=False,
            path='/', path_specified=True,
            secure=False, expires=None,
            discard=True, comment=None, comment_url=None, rest={}
        )
        cookies.set_cookie(cookie)

def openlink(browser, post_link):
    try:
        r = browser.open(post_link)
        return r
    except Exception as e:
        print(f"Error opening the link: {str(e)}")
        return None

def post_comment(browser, comment_text):
    try:
        browser.select_form(nr=0)
        browser.form['comment_text'] = comment_text
        browser.submit()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Comment posted: {comment_text} at {current_time}")
        return True
    except Exception as e:
        print(f"Error posting comment: {str(e)}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        post_link = request.form['post_link']
        number_of_cookies = int(request.form['number_of_cookies'])
        json_cookies_list = [request.form[f'json_cookie_{i+1}'] for i in range(number_of_cookies)]
        comment_file = request.files['comment_file']
        delay_time = int(request.form['delay_time'])

        comments = comment_file.read().decode('utf-8').splitlines()

        for json_cookies in json_cookies_list:
            cookies = mechanize.CookieJar()
            browser = mechanize.Browser()
            browser.set_handle_robots(False)
            browser.set_handle_refresh(False)

            for key, value in g_headers.items():
                browser.addheaders.append((key, value))

            load_cookies_from_json(json_cookies, cookies)
            browser.set_cookiejar(cookies)

            if openlink(browser, post_link):
                for comment in comments:
                    if len(comment) > 0:
                        success = post_comment(browser, comment)
                        if success:
                            print(f"JSON Cookie no {json_cookies_list.index(json_cookies) + 1} comment sent successfully ✅")
                        time.sleep(delay_time)

        return "Comments posted successfully!"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
