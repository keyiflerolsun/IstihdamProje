from bs4 import BeautifulSoup
from more_itertools import peekable
from .article import ArticleLink
from .wikiutil.wikiutil import *
import re

import requests

class WikiSearcher:

    def __init__(self):            
        self.__URL_ROOT = 'https://en.wikipedia.org'
        self.__URL_SEARCH = 'https://en.wikipedia.org/wiki'
    
    def search(self, search, verbose=False):
        search_url = ''
        if isinstance(search, ArticleLink):
            if search.link is None:
                return search.name
            search_url = self.__URL_ROOT + search.link
        else:
            search_replaced = search.replace(' ', '_')
            search_url = self.__URL_SEARCH + f'/{search_replaced}'
        raw_html = requests.get(search_url).text
        soup = BeautifulSoup(raw_html, 'lxml')
        body_content = soup.find('div', class_='mw-parser-output')
        if body_content is None:
            return False
        if 'most often refers to:' not in soup.text and 'may also refer to:' not in soup.text and 'may refer to:' not in soup.text:
            description = self.get_description_p_tag(body_content, verbose)
            return description
        else:
            wiki_clean_option(body_content)
            body_children = []
            for child in body_content.children:
                if child.name is not None and child.name not in ['style', 'h3', 'h4']:
                    body_children.append(child)
            wiki_clean_option_p(body_children)
            peekable_children = peekable(body_children)
            options = {}
            prev_key = None
            for child in peekable_children:
                peek_child = None
                try:
                    peek_child = peekable_children.peek()
                except StopIteration:
                    pass
                if child.name == 'p' and peek_child.name == 'h2':
                    continue
                if child.name == 'p' or child.name == 'h2':
                    prev_key = child.text.strip()
                    a_tag = child.find('a')
                    if a_tag is not None:
                        prev_key = f'{prev_key} (already a description select for more info.)'
                        options[prev_key] = []
                        article_link = ArticleLink(a_tag.attrs['title'], a_tag.attrs['href'])
                        options[prev_key].append(article_link)
                    else:
                        if peek_child.name  in ['p', 'h2']:
                            prev_key = f'{prev_key} (already a description)'
                            options[prev_key] = None


                else:
                    options[prev_key] = []
                    ul_tags = []
                    ul_tags.append(child)
                    try:
                        while peek_child is not None and peek_child.name == 'ul':
                            ul_tags.append(next(peekable_children))
                            peek_child = peekable_children.peek()
                        
                    except StopIteration:
                        pass
                    li_tags = []
                    for ul in ul_tags:
                        lis = ul.find_all('li', recursive=False)
                        if lis is not None:
                            li_tags.extend(lis)
                    for li in li_tags:
                        a_tag = has_link(li)
                        if a_tag is None:
                            #options[prev_key].append(li.text + ' (no other link)')
                            article_link = ArticleLink(li.text + ' (no other link)', None)
                        else:
                            article_link = ArticleLink(a_tag.attrs['title'], a_tag.attrs['href'])
                            #options[prev_key].append(article_link)
                        options[prev_key].append(article_link)

            return options
                            
    def get_description_p_tag(self, body_content, verbose=False):
        p_tags = body_content.find_all('p', attrs={'class': None}, recursive=False)
        description = p_tags[0].text
        if not verbose:
            pass
        else:
            if len(p_tags) > 1:
                description = p_tags[0].text + p_tags[1].text
        description = re.sub(r'\[\d+\]', '', description)
        return description                       
                              
                
                
            
            
            
            

        
        
