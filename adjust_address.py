def ucf_title(string):
    parts = string.split()
    new_string = ""
    for part in parts:
        if part != "UCF":
            new_string += part.title() + " "
        else:
            new_string += part + " "
    return new_string.strip()

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
        
        return ucf_title(txt)
            
# tests = [
#     "5436 SILVER KNIGHT WAY",
#     "3438 KNIGHTS KROSSING CIR",
#     "4323 GOLDEN KNIGHT CIR",
#     "1232 BLACK KNIGHT DR",
#     "1324 COLLEGE KNIGHT CT",
#     "2454 COLLEGE PARK TRAIL",
#     
#     "34432 NORTH GOLDENROD RD",
#     "12998 GEMINI BLVD",
#     "12345 GEMINI BLVD W"
# ]
# 
# for test in tests:
#     print('$'+replace_address(test)+'$')
