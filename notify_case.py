# Replaces words spelled incorrectly
def replace_word(word, replace_words):
    word = word.lower()
    if word in replace_words.keys():
        return replace_words[word]
    else:
        return word

# Exceptions to .title()
def title_except(string, excepts):
    parts = string.split()
    new_string = ""
    for part in parts:
        if part not in excepts:
            new_string += part.title() + " "
        else:
            new_string += part + " "
    return new_string.strip()

def notify_case(case):
    from send_telegram import sendTeleg
    from configparser import ConfigParser
    from meta_toolkit import post_to_meta_both
    from adjust_address import replace_address
    from datetime import datetime
    import json
        
    with open('constants.json', encoding="utf8") as f:
        constants = json.load(f)

    main_config = ConfigParser()
    main_config.read('config.ini')
    generate_image(case, main_config.get("GOOGLE", "API_KEY"))

    emojis: dict = constants['emoji_pairs']
    replace_words = constants['replace_words']
        
    # Fix title
    title = ''
    for word in case['type'].split():
         title += title_except(replace_word(word, replace_words), ["DUI", "DL", "NOS"])
         title += ' '

    # Add emojis to end of title
    emoji_suffix = ''
    for emoji_txt in emojis.keys():
        if emoji_txt in title.lower():
             emoji_suffix += f'{emojis[emoji_txt]}' # Must use += and not .join() to preserve encoding
    title += emoji_suffix

    # Change to 12hr time
    reported = datetime.strptime(case['reported_dt'], '%m/%d/%y %H:%M').strftime('%m/%d/%y %I:%M %p')
    start = datetime.strptime(case['occur_start'], '%m/%d/%y %H:%M').strftime('%m/%d/%y %I:%M %p')
    end = datetime.strptime(case['occur_end'], '%m/%d/%Y %H:%M').strftime('%m/%d/%y %I:%M %p')

    message = f"""{title}
Case: #{case['case_id']} reported on {reported}
Occured at {title_except(case['campus'], ["UCF"])}, {title_except(replace_address(case['location']), ["UCF", "UCFPD"])}
Between {start} - {end}
Status: {case['disposition'].title()}"""

    print(message)
    print()

    photo = open('caseout.png', "rb")
    if main_config.getboolean("META", "ENABLE"):
        post_to_meta_both(main_config.get("META", "FB_PAGE_ID"), main_config.get("META", "IG_USER_ID"), 'caseout.png', message, main_config.get("META", "ACCESS_TOKEN"))
    if main_config.getboolean("TELEGRAM", "ENABLE"):
        sendTeleg(message, main_config, photo)
    return None


def generate_image(case,key):
    import googlemaps
    import staticmaps
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_OSM)
#
    gmaps_key = googlemaps.Client(key=key)
    g = gmaps_key.geocode(f'{case["location"].replace("/", "")} Orlando FL, US.')
    lat = g[0]["geometry"]["location"]["lat"]
    long = g[0]["geometry"]["location"]["lng"]
    loc = staticmaps.create_latlng(lat, long)
    context.add_object(staticmaps.Marker(loc, color=staticmaps.RED, size=12))
    # render anti-aliased png (this only works if pycairo is installed)
    image = context.render_cairo(380, 380)
    image.write_to_png("case.png")
    # render anti-aliased png (this only works if pycairo is installed)
    context.set_zoom(18)
    image = context.render_cairo(1080, 1080)
    image.write_to_png("casez.png")
    from PIL import Image, ImageDraw, ImageFilter
    im1 = Image.open('casez.png')
    im2 = Image.open('case.png')
    im1.paste(im2, (700, 700))
    draw = ImageDraw.Draw(im1)
    #Vert
    draw.line((700, 700, 700, 1080), fill=(0, 0, 0), width=10)
    #Horz
    draw.line((696, 700, 1080, 700), fill=(0, 0, 0), width=10)
    im1.save('caseout.png', quality=100)