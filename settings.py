ATTR_NAME_DICT = {
    'itemprop': {
        'articleBody': 'articleBody',
        'headline': 'headline',
        'description': 'description',
        'alternativeHeadline': 'alternativeHeadline',
    },
}
ATTR_SCHEME_DICT = {
    'itemtype': {
        'http://schema.org/NewsArticle': 'http://schema.org/NewsArticle',
        'http://schema.org/Article': 'http://schema.org/Article',
        'https://schema.org/Article': 'https://schema.org/Article',
    }
}

TEXT_TAG_DICT = {
    'h1': 'h1',
    'p': 'p',
    'a': 'a',
    'div': 'div',
    'span': 'span',
    'div': 'div',
    'article': 'article'
}

LINK_TAG_DICT = {
    'a': 'a',
    'span': 'span',
}

# TAG_DICT = {
#     'div': 'div',
#     'article': 'article',
# }

FILTERS_CONTAINS = {
    'class': (
        'favorite',
        'b-box',
        'dark',
        'social',
        'video',
        'meta',
    ),
    'itemprop': (
        'date',
        'rating',
        'Rating',
        'name',
        'Name',
    ),
}

FILTERS_MATCH = {
    'class': (
        'title',
        'item',
    ),
    'itemprop': (
        'articleSection',
    ),
}

FILTERS_CONTAINS_DATA = (
    'window._',
    'window[',
    'if',
    ': "',
    'meta',
)
