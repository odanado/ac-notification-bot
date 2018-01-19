import time
import requests
import slackweb
import click
from logzero import logger


ENDPOINT = 'http://kenkoooo.com/atcoder/atcoder-api/results'


def fetch_new_ac(users, threshold):
    payload = {'user': users[0], 'rivals': ','.join(users[1:])}
    res = requests.get(ENDPOINT, params=payload)
    results = res.json()
    results = [x for x in results if x['result'] == 'AC']
    results = sorted(results, key=lambda x: x['epoch_second'], reverse=True)

    results = [x for x in results if x['epoch_second'] > threshold]

    return results


def format_result(result):
    url = ('https://beta.atcoder.jp/contests/'
           '{0[contest_id]}/tasks/{0[problem_id]}').format(result)
    text = ('{0[user_id]} が {1} を{0[language]} でACしたよ！'.format(result, url))
    return text


@click.command()
@click.option('--users', type=str, envvar='users')
@click.option('--webhook', envvar='WEBHOOK')
@click.option('--threshold', type=int, envvar='THRESHOLD')
def cmd(webhook, users, threshold):
    slack = slackweb.Slack(url=webhook)
    users = users.split(',')
    threshold = time.time() - threshold
    results = fetch_new_ac(users, threshold)

    for result in results:
        text = format_result(result)
        logger.info('notice: ' + text)
        slack.notify(text=text, username='AC bot', icon_emoji=':ac:')


def main():
    cmd()


if __name__ == '__main__':
    main()
