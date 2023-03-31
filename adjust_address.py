def expand_address(txt):
    import re
    txt = ' ' + txt + ' '
    presubs = {
        ' W\.? ': ' WEST ',
        ' E\.? ': ' EAST ',
        ' N\.? ': ' NORTH ',
        ' S\.? ': ' SOUTH ',
    }
    for key, value in presubs.items():
        txt = re.sub(key, value, txt)
    return txt.strip()

# Will work despite differing word positions
# Needs to be robust string matching function
def replace_address(txt):
    import json
    import editdistance

    TYPO_TOLERANCE = 1

    txt = expand_address(txt)
    txt_tokens = txt.split()

    with open('locations.json') as f:
        locs = json.load(f)

        # Do this with every key
        for key in locs.keys():
            key_tokens = key.split()

            # Assume true until proven false
            is_match = True

            # If numerical start, make sure it matches
            if txt_tokens[0][0] in '0123456789' and key_tokens[0][0] in '0123456789' and txt_tokens[0] != key_tokens[0]:
                is_match = False
                continue

            # Go through each token in key
            for key_token in key_tokens:
                token_distances = [editdistance.eval(key_token, txt_token) for txt_token in txt_tokens]
                if min(token_distances) > TYPO_TOLERANCE:
                    is_match = False
                    break

                # if key_token not in txt_tokens:
                #     is_match = False
                #     break

            # If all tokens match, locations is found
            if is_match:
                return locs[key]
        
        # Otherwise return original
        return txt