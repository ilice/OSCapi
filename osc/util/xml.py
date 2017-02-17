from osc.util import num

__all__ = ['xml_to_json']


def xml_to_json(element, lists=(), forced_int=()):
    json_element = dict()
    for child in element:
        tag = child.tag.split('}')[-1]
        json_child = xml_to_json(child, lists, forced_int=forced_int)

        if tag in lists:
            json_element[tag] = (json_element[tag] if tag in json_element else []) + [json_child]
        else:
            json_element[tag] = json_child

    if len(json_element) == 0:
        json_element = None
        if element.text is not None:
            if element.tag.split('}')[-1] in forced_int:
                try:
                    json_element = num(element.text) if len(str(num(element.text))) == len(element.text) else element.text
                except ValueError:
                    json_element = element.text
            else:
                json_element = element.text

    return json_element
