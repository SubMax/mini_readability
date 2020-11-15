LINE_WIDTH = 79

ATTR_NAME_DICT = {
    'itemprop': {
        'articleBody': 'articleBody',
        'headline': 'headline',
        'description': 'description',
        'alternativeHeadline': 'alternativeHeadline',
    },
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
}

FILTERS_CONTAINS = {
    'class': (
        'favorite',
        'box',
        'dark',
        'social',
        'video',
        'meta',
        'count',
        'credits',
        'photo',
        'media',
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

FILTERS_MATCH_DATA = (
    'Реклама',
)