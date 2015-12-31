
def prepare_query_params(params):
    kwargs = {}
    for param in params:
        if param == 'type':
            kwargs['issue_type'] = params[param][0]
        elif param == 'status':
            kwargs['status'] = params[param][0]
        elif param == 'tag':
            kwargs['tags__id'] = params[param][0]
        elif param == 'created_by':
            kwargs['created_by__pk'] = params[param][0]
    return kwargs


def smart_list(value, delimiter=",", func=None):
    """Convert a value to a list, if possible.

    Args:
        value: the value to be parsed. Ideally a string of comma separated
            values - e.g. "1,2,3,4", but could be a list, a tuple, ...

    Kwargs:
        delimiter: string, the delimiter used to split the value argument,
            if it's a string / unicode. Defaults to ','.
        func: a function applied to each individual element in the list
            once the value arg is split. e.g. lambda x: int(x) would return
            a list of integers. Defaults to None - in which case you just
            get the list.

    Returns: a list if one can be parsed out of the input value. If the
             value input is an empty string or None, returns an empty
             list. If the split or func parsing fails, raises a ValueError.

    This is mainly used for ensuring the CSV model fields are properly
    formatted. Use this function in the save() model method and post_init()
    model signal to ensure that you always get a list back from the field.

    """
    if value in ["", u"", "[]", u"[]", u"[ ]", None]:
        return []

    if isinstance(value, list):
        l = value
    elif isinstance(value, tuple):
        l = list(value)
    elif isinstance(value, basestring) or isinstance(value, unicode):
        # TODO: regex this.
        value = value.lstrip('[').rstrip(']').strip(' ')
        if len(value) == 0:
            return []
        else:
            l = value.split(delimiter)
    elif isinstance(value, int):
        l = [value]
    else:
        raise ValueError(u"Unparseable smart_list value: %s" % value)

    try:
        func = func or (lambda x: x)
        return [func(e) for e in l]
    except Exception as ex:
        raise ValueError(u"Unable to parse value '%s': %s" % (value, ex))