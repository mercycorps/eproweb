
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


