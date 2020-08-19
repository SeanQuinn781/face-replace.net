import random


def get_emoji_size(h, w):
    if h < 57 or w < 57:
        # 37px imgs
        return "small-small/"
    elif h < 95 or w < 95:
        # 75px imgs
        return "small/"
    elif h < 132 or w < 132:
        # 112px imgs
        return "medium-small/"
    elif h < 190 or w < 190:
        # 150px imgs
        return "medium/"
    else:
        # use default 300x300px for anything larger
        return False


def select_emoji():
    emojis = [
        "surprise.png",
        "sadness.png",
        "neutral.png",
        "disgust.png",
        "anger.png",
        "happy.png",
    ]
    emoji = random.sample(emojis, 1)[0]

    return emoji


if __name__ == "__main__":
    main()
