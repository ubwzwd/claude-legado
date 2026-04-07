import sys
from novel.commands import dispatch


def main():
    args = sys.argv[1:]
    dispatch(args)


if __name__ == "__main__":
    main()
