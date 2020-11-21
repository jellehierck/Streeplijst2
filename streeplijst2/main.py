from argparse import ArgumentParser

from streeplijst2 import create_app
from streeplijst2.config import PORT

if __name__ == '__main__':
    # Use the argparse library to handle support for command line options when running the app from a console
    parser = ArgumentParser(prog='Streeplijst2',
                            description='Paradoks streeplijst application, created by Jelle Hierck.')

    # Hostname argument (e.g. localhost, 127.0.0.1, 123.456.78.90)
    parser.add_argument('host',
                        nargs='?',
                        default='localhost',
                        help='hostname for this app. Default: localhost')

    # Port nr argument (e.g. 5000)
    parser.add_argument('-p',
                        '--port',
                        type=int,
                        default=PORT,
                        help='port number for this app')

    # Run in debug mode argument
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        # Defaults to False
                        help='run this app in debug mode')

    args = parser.parse_args()  # Parse the arguments

    app = create_app()  # Create flask app
    app.run(host=args.host, port=args.port, debug=args.debug)
