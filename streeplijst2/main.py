from argparse import ArgumentParser

from streeplijst2 import create_app
from streeplijst2.config import PORT

if __name__ == '__main__':
    parser = ArgumentParser(prog='Streeplijst2',
                            description='Paradoks streeplijst application, created by Jelle Hierck.')

    parser.add_argument('host',
                        nargs='?',
                        default='localhost',
                        help='hostname for this app. Default: localhost')

    parser.add_argument('-p',
                        '--port',
                        type=int,
                        default=PORT,
                        help='port number for this app')

    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        # Defaults to False
                        help='run this app in debug mode')

    args = parser.parse_args()

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)
    app.run()
