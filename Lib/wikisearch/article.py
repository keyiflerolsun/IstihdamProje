class ArticleLink:
    def __init__(self, name, link):
        self.__name = name
        self.__link = link

    @property
    def name(self):
        return self.__name
    @property
    def link(self):
        return self.__link

    def __str__(self):
        return self.__link
