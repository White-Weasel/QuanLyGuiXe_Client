import winsound


def annoy():
    for i in range(1, 10):
        winsound.Beep(i * 100, 200)


def beep_beep():
    winsound.Beep(2500, 150)
    winsound.Beep(2500, 150)


if __name__ == '__main__':
    winsound.Beep(2500, 150)
    winsound.Beep(2500, 150)
    # winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
