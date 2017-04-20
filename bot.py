from slacker import Slacker
import datetime
import socket
import ssl
import slack_settings


slack = Slacker(slack_settings.SLACK_API_TOKEN)


def ssl_valid_time_remaining(hostname):
    expires = ssl_expiry_datetime(hostname)
    return expires - datetime.datetime.utcnow()


def ssl_expires_in(hostname, buffer_days=7):
    remaining = ssl_valid_time_remaining(hostname)
    if remaining < datetime.timedelta(days=0):
        raise AlreadyExpired("Cert expired %s days ago" % remaining.days)
    elif remaining < datetime.timedelta(days=buffer_days):
        return True
    else:
        return False


def ssl_expiry_datetime(hostname):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
    context = ssl.create_default_context()

    conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=hostname,
    )

    conn.settimeout(3.0)
    conn.connect((hostname, 443))
    ssl_info = conn.getpeercert()
    return datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)


def post_slack(hostname):
    message = '@channel https://' + hostname + ' '
    if ssl_expires_in(hostname):
        message += 'そろそろヤバイ'
    else:
        message += 'はまだ期限内' 

    slack.chat.post_message(
            '#expiration',
            message,
            as_user=True,
            link_names=True
    )

if __name__ == '__main__':
    post_slack('nnsnodnb.moe')
    post_slack('twidule.nnsnodnb.moe')

