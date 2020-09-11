from flask_caching import Cache

# Caching for temporarily storing results of time-consuming requests (e.g. get folders)
cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})
