def notify_case(case):
    from send_telegram import sendTeleg
    from configparser import ConfigParser
    from meta_toolkit import post_to_meta_both
    from adjust_address import replace_address
    
    main_config = ConfigParser()
    main_config.read('config.ini')
    generate_image(case, main_config.get("GOOGLE", "API_KEY"))
    emoji_pairs = {"cannabis": "🌿🚬", "dui": "🍸🚗", "reckless drving": "💥🚗", "traffic": "🚗🚓", "counterfeit dl": "🪪🆔", "license": "🪪🆔"}
    fun_type = case['type'].title()
    for word, emoji in emoji_pairs.items():
        if word in case['type'].lower():
            fun_type = case['type'].title() + " " + emoji


    message = f"""{fun_type}
Case#: ({case['case_id']}) reported at {case['reported_dt']}.
Occured at {ucf_title(case['campus'])}, {replace_address(case['location'])}
At times: {case['occur_start']} - {case['occur_end']}
Status is {case['disposition'].title()}."""
    photo = open('caseout.png', "rb")
    if main_config.getboolean("META", "ENABLE"):
        post_to_meta_both(main_config.get("META", "FB_PAGE_ID"), main_config.get("META", "IG_USER_ID"), 'caseout.png', message, main_config.get("META", "ACCESS_TOKEN"))
    if main_config.getboolean("TELEGRAM", "ENABLE"):
        sendTeleg(message, main_config, photo)
    return None

def ucf_title(string):
    parts = string.split()
    new_string = ""
    for part in parts:
        if part != "UCF":
            new_string += part.title() + " "
        else:
            new_string += part + " "
    return new_string.strip()

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
    draw.line((700, 700, 700, 1080), fill=(0, 0, 0), width=10)
    draw.line((700, 700, 1080, 700), fill=(0, 0, 0), width=10)
    im1.save('caseout.png', quality=100)