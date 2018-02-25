import simplejson


def valid_json(input):
    """ Return true/false depending on whether input is valid JSON """
    is_valid = False
    try:
        simplejson.loads(input)
        is_valid = True
    except:
        pass

    return is_valid
