def expand_address(txt):
    import re
    txt = ' ' + txt + ' '
    presubs = {
        ' W\.? ': ' WEST ',
        ' E\.? ': ' EAST ',
        ' N\.? ': ' NORTH ',
        ' S\.? ': ' SOUTH ',
        'BLD' : 'BLVD'
    }
    for key, value in presubs.items():
        txt = re.sub(key, value, txt)
    return txt.strip()

def replace_address(txt):
    import json
    txt = expand_address(txt)

    with open('locations.json') as f:
        locs = json.load(f)
        for key in locs.keys():
            if key in txt:
                return locs[key]  
        
        return txt