import argparse
import os
import sys


def cmd():
    args = sys.argv[1:]
    print(f'🐍 → args={args}')  # noqa: T201
    os.system(' '.join(args))


class CustomHelpFormatter(argparse.HelpFormatter):
    def _get_help_string(self, action):
        help_text = action.help
        if help_text is not None and '%(default)' not in help_text:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    help_text += ' (default: %(default)s)'
        return help_text


def prepare():
    os.system('git config core.hooksPath .githook')
    pass


def install():
    parser = argparse.ArgumentParser(
        description='Install Tool', formatter_class=CustomHelpFormatter
    )
    parser.add_argument(
        '--scope',
        default='all',
        choices=['all', 'rt'],
        help='Install all dependencies or runtime dependencies or development dependencies',
    )
    args = parser.parse_args()
    print(f'🐍 → args={args}')  # noqa: T201
    cmd = 'uv sync'
    if args.scope == 'all':
        cmd += ' --extra dev'

    os.system(cmd)
    pass


def lint():
    parser = argparse.ArgumentParser(description='Lint Tool')
    parser.add_argument(
        '--fix',
        action='store_true',
        default=False,
        help='auto fix format or lint problems',
    )
    parser.add_argument(
        '--type', action='store_true', default=True, help='run type check'
    )
    args = parser.parse_args()
    print(f'🐍 → args={args}')  # noqa: T201
    if args.fix:
        print('🐍 → auto fix format or lint problems')
        os.system('.venv/bin/ruff check --fix')
    else:
        print('🐍 → run format or lint check')
        os.system('.venv/bin/ruff check --diff')
        if args.type:
            print('🐍 → run type check')
            os.system('.venv/bin/pyright')
    pass


