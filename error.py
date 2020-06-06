import colorama


colorama.init()


def prepare_article_error(error):
    print(colorama.Fore.RED + "Error: {0}".format(error) + colorama.Style.RESET_ALL)