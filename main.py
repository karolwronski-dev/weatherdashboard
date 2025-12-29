from utils import *


def main():
    is_first_time, user_name = get_user_info()

    if is_first_time:
        print(f"Nice to meet You, {user_name}! Let me configure dashboard...")
    else:
        print(f"Welcome again, {user_name}! Loading...")


if __name__ == "__main__":
    main()
