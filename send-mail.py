def parseargs():
    "parse arguments"
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", default="manictime.example.com")
    parser.add_argument("-s", "--scheme", default="https")
    parser.add_argument("-u", "--user")
    parser.add_argument("-p", "--password")
    parser.add_argument("--log-level", choices=["debug", "info", "warn", "error", "fatal"], default="info")
    parser.add_argument("lists", nargs="+")
    return parser.parse_args()


def login(**kwargs):
    "login with an account"
    import requests
    import logging
    import getpass
    if not kwargs['password']:
        kwargs['password'] = getpass.getpass(prompt="Seems like you didnot specify password in cmd or specified an "
                                                    "empty password.\nInput the password or leave it empty")
    logging.info("login to {host}...".format(**kwargs))
    param = kwargs
    logging.debug("login with {}".format(str(param)))
    response = requests.post("{scheme}://{host}/account/login".format(**kwargs), json=param)
    if response.status_code == 200:
        logging.info("logged-in successfully")
        return response.cookies['.AspNetCore.Cookies']
    elif response.status_code == 401:
        raise Exception("Wrong password")
    else:
        raise Exception("Server respond with code {}".format(response.status_code))


def get(**kwargs):
    import requests
    response = requests.get("{scheme}://{host}/users/getByUsername".format(**kwargs), params={'username': kwargs['username']}, cookies=kwargs['cookies'])
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 204:
        return False
    else:
        raise Exception("Unexpected Server response: {}".format(response.status_code))


def sendmail(**kwargs):
    import requests
    response = requests.post("{scheme}://{host}/Users/SendActivationMail".format(**kwargs), cookies=kwargs['cookies'], data={
        "userId": kwargs['userId']
    })
    if response.status_code != 200:
        raise Exception(response.content)
    return True

def main(args):
    """main func"""
    import logging
    logging.basicConfig(level=logging.getLevelName(args.log_level.upper()))
    cookies = {'.AspNetCore.Cookies':
                   login(scheme=args.scheme, host=args.host, username=args.user, password=args.password)}
    for listfile in args.lists:
        userlist = [line.strip().split(",") for line in open(listfile, encoding="utf-8")]
        for name, email in userlist:
            name,email = name.strip(), email.strip()
            user =  get(username=email, scheme=args.scheme, host=args.host, cookies=cookies)
            if not user: # no user
                logging.warning("User with email {} doesn't exist".format(email))
            elif user['activeStatus'] == 1: # not activated
                print(email, sendmail(userId=user['userId'], scheme=args.scheme, host=args.host, cookies=cookies))


if __name__ == "__main__":
    main(parseargs())
