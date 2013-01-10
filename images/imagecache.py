"""
max_cache_len = nb mx images in cache = hard coded variable
min_request_nb_to_cache = min nb of requests before going in cache = hard coded variable
least_used_cached_image = image in the cache that is the least requested

have list of all images in memcache
each image in memcache should have nb_requests

when serving image
    increase memcache_image_list[image].nb_requests
    if not in cache:
        if image.nb_requests > min_request_nb_to_cache and cache_size < max_cache_len:
            put image in cache
        elif image.nb_requests > least_used_cached_image.nb_requests:
            remove least_used_cached_image from cache
            put image in cache
    serve image

when adding image to cache
    if image.nb_requests < least_used_cached_image:
        least_used_cached_image = image
"""
