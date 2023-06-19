from configparser import ConfigParser
from meta_toolkit import post_to_meta_both
from datetime import datetime
from send_telegram import sendTeleg
import string_adjustments as stradj

def notify_case(case):
    # Read the config
    main_config = ConfigParser()
    main_config.read('config.ini')

    # Reformat dates and times
    reported = datetime.strptime(case['reported_dt'], '%m/%d/%y %H:%M').strftime('%m/%d/%y %I:%M %p')
    start = datetime.strptime(case['occur_start'], '%m/%d/%y %H:%M').strftime('%m/%d/%y %I:%M %p')
    end = datetime.strptime(case['occur_end'], '%m/%d/%Y %H:%M').strftime('%m/%d/%y %I:%M %p')

    # Get the emojis from the formatted title
    # This should already have stradj.case_title_format applied to it
    case_emojis = stradj.get_emojis(case['type'])
    # This should have gpt_expand.gpt_title_expand applied to it
    long_title = case['explained_title']

    # Append the emojis to the title (includes space already)
    case_title = long_title + case_emojis

    # Assumes replace_address has already been applied
    disp_addr = case['display_address']

    # Compose message
    message = f"""{stradj.gen_title(case_title)}
Case #: {case['case_id']} reported on {reported}
Occured at {stradj.gen_title(case['campus'])}, {disp_addr}
Between {start} - {end}
Status: {stradj.gen_title(case['disposition'])}"""

    print(message)
    print()


    # Create the image
    generate_image(case, main_config.get("GOOGLE", "API_KEY"))

    # Post to socials
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