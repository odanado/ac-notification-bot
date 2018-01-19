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
@click.argument('users_file', type=str)
@click.option('--webhook', envvar='WEBHOOK')
@click.option('--threshold', type=int, default=10*60)
def cmd(webhook, users_file, threshold):
    slack = slackweb.Slack(url=webhook)
    users = [line.strip() for line in open(users_file)]
    threshold = time.time() - threshold
    results = fetch_new_ac(users, threshold)

    for result in results:
        text = format_result(result)
        logger.info('notice: ' + text)
        slack.notify(text=text, icon_emoji=':ac:')


def main():
    cmd()


if __name__ == '__main__':
    main()
