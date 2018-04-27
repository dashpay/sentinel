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


def extract_object(json_input):
    """
    Given either an old-style or new-style Proposal JSON string, extract the
    actual object used (ignore old-style multi-dimensional array and unused
    string for object type)
    """
    if not valid_json(json_input):
        raise Exception("Invalid JSON input.")

    obj = simplejson.loads(json_input, use_decimal=True)

    if (isinstance(obj, list) and
        isinstance(obj[0], list) and
        (isinstance(obj[0][0], str) or (isinstance(obj[0][0], unicode))) and
        isinstance(obj[0][1], dict)):
        obj = obj[0][1]

    return obj
