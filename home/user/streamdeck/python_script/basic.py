#!/usr/bin/env python3

#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#
## https://github.com/abcminiuser/python-elgato-streamdeck/tree/master

# Example script showing basic library usage - updating key images with new
# tiles generated at runtime, and responding to button state change events.

import os
import threading
import requests
import json
import time

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.Transport.Transport import TransportError

# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")



api_start_url = "http://127.0.0.1/api/start"
api_stop_url = "http://127.0.0.1/api/stop"
api_new_event_url = "http://127.0.0.1/api/change/622ddd?title=new-title&cue=new-cue"
api_blackout_url_false = "http://127.0.0.1/api/message/timer?blackout=false"
api_blackout_url_true = "http://127.0.0.1/api/message/timer?blackout=true"
api_add10_url = "http://127.0.0.1/api/addtime/add/600"
api_remove10_url = "http://127.0.0.1/api/addtime/remove/600"
api_add5_url = "http://127.0.0.1/api/addtime/add/300"
api_remove5_url = "http://127.0.0.1/api/addtime/remove/300"
api_add1_url = "http://127.0.0.1/api/addtime/add/60"
api_remove1_url = "http://127.0.0.1/api/addtime/remove/60"
api_blink_url_false = "http://127.0.0.1/api/message/timer?blink=false"
api_blink_url_true = "http://127.0.0.1/api/message/timer?blink=true"
api_load_first_url = "http://127.0.0.1/api/load/index/1"
api_reload_url = "http://127.0.0.1/api/reload"

data_rundown_url = "http://127.0.0.1/data/rundown"



# Generates a custom tile with run-time generated text and custom image via the
# PIL module.
def render_key_image(deck, icon_filename, font_filename, label_text):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    icon = Image.open(icon_filename)
    image = PILHelper.create_scaled_key_image(deck, icon, margins=[0, 0, 20, 0])

    # Load a custom TrueType font and use it to overlay the key index, draw key
    # label onto the image a few pixels from the bottom of the key.
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_filename, 14)
    draw.text((image.width / 2, image.height - 5), text=label_text, font=font, anchor="ms", fill="white")

    return PILHelper.to_native_key_format(deck, image)


# Returns styling information for a key based on its position and state.
def get_key_style(deck, key, state):
    # Last button in the example application is the exit button.
    exit_key_index = deck.key_count() - 1

    if key == exit_key_index:
        name = "exit"
        icon = "{}.png".format("Exit")
        font = "Roboto-Regular.ttf"
        label = "Bye" if state else "Exit"
    else:
        name = "emoji"
        icon = "{}.png".format("Pressed" if state else "Released")
        font = "Roboto-Regular.ttf"
        label = "Pressed!" if state else "Key {}".format(key)

## https://www.flaticon.com/authors/special/lineal-color?author_id=1&type=standard

    match key:
        case 0:
            icon = "multimedia.png"#.format("Pressed" if state else "Released")
            label = "Pressed!" if state else "Start".format(key)
        case 1: 
            icon = "stop.png"#.format("Pressed" if state else "Released")
            label = "Pressed!" if state else "Stop".format(key)
        case 2:
            icon = "add.png"#.format("Pressed" if state else "Released")
            label = "Pressed!" if state else "+1".format(key)
        case 3:
            icon = "add.png"#.format("Pressed" if state else "Released")
            label = label = "Pressed!" if state else "+5".format(key)    
        case 4:
            icon = "add.png"#.format("Pressed" if state else "Released")
            label = label = "Pressed!" if state else "+10".format(key)
        case 5:
            icon = "car-wash.png"#.format("Pressed" if state else "Released")
            label = label = "Pressed!" if state else "Cleanup".format(key)
        case 6:
            icon = "wall-clock.png"#.format("Pressed" if state else "Released")
            label = label = "Pressed!" if state else "Uhr".format(key)
        case 7:
            icon = "remove.png"#.format("Pressed" if state else "Released")
            label = label = "Pressed!" if state else "-1".format(key)   
        case 8:
            icon = "remove.png"#.format("Pressed" if state else "Released")
            label = label = "Pressed!" if state else "-5".format(key)         
        case 9:
            icon = "remove.png"#.format("Pressed" if state else "Released")
            label = label = "Pressed!" if state else "-10".format(key)
        case 10:
            icon = "flash.png"#.format("Pressed" if state else "Released")
            label = label = "Pressed!" if state else "Flash".format(key)
        case 11:
            icon = "flash-off.png"#.format("Pressed" if state else "Released")
            label = label = "Pressed!" if state else "no Flash".format(key)
        case 12:
            icon = "hide.png"#.format("Pressed" if state else "Released")
            label = "Pressed!" if state else "Blackout".format(key)
        case 13:
            icon = "show.png"#.format("Pressed" if state else "Released")
            label = "Pressed!" if state else "no Blackout".format(key)


    return {
        "name": name,
        "icon": os.path.join(ASSETS_PATH, icon),
        "font": os.path.join(ASSETS_PATH, font),
        "label": label
    }



# Creates a new key image based on the key index, style and current key state
# and updates the image on the StreamDeck.
def update_key_image(deck, key, state):
    # Determine what icon and label to use on the generated key.
    key_style = get_key_style(deck, key, state)

    # Generate the custom key with the requested image and label.
    image = render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"])
  
    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)


# Prints key state change information, updates rhe key image and performs any
# associated actions when a key is pressed.
def key_change_callback(deck, key, state):
    # Print new key state
    print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)
    try:
        match state:
            case True:
                match key:
                    case 0: ### Starten
                        response = requests.get(api_start_url)
                        print(response)
                    case 1: ### Stoppen und zurückstellen
                         ## ausblenden
                        requests.get(api_blackout_url_true)

                        time.sleep(0.5)

                        requests.get(api_reload_url)
                        time.sleep(0.5)
                         ## einblenden
                        requests.get(api_blackout_url_false)

                    case 2: ### +1 Minute
                        response = requests.get(api_add1_url)
                        print(response)
                        
                    case 3: ### +5 Minuten
                        response = requests.get(api_add5_url)
                        print(response)
                    case 4: ### + 10 Minuten
                        response = requests.get(api_add10_url)
                        print(response)
                    case 5: ### Event auf 10 Minuten zurückstellen und laden
                        ## ausblenden
                        requests.get(api_blackout_url_true)

                        time.sleep(0.5)

                        ## Rundown abfragen
                        response = requests.get(data_rundown_url)
                        print(response.request.headers)
                        print(response.text)
                        
                        ## event id des ersten events herrausfinden
                        
                        data = json.loads(response.text)
                        event_id = data[0]["id"]
                        print(f"event ID {event_id}")

                        ## Timer stoppen
                        requests.get(api_stop_url)

                        ## event 1 sauber machen und auf 10 Minuten stellen
                        api_cleanup_first_url = f"http://127.0.0.1/api/change/{event_id}?title=&cue=&duration=600&skip=false&timerType=count-down"
                        cleanup_response = requests.get(api_cleanup_first_url)
                        print(cleanup_response)

                        time.sleep(0.5) 

                        ## Event 1 laden
                        r = requests.get(api_load_first_url)
                        print(f"load first: {r}")

                        ## einblenden
                        requests.get(api_blackout_url_false)

                    case 6: ### Uhr Einblenden
                        ## ausblenden
                        requests.get(api_blackout_url_true)

                        time.sleep(0.5)

                        response = requests.get(data_rundown_url)
                        print(response.request.headers)
                        print(response.text)
                        ## event id des ersten events herrausfinden
                        
                        data = json.loads(response.text)
                        event_id = data[0]["id"]
                        print(f"event ID {event_id}")

                        ## Timer stoppen
                        requests.get(api_stop_url)



                        ## event 1 sauber machen und auf 10 Minuten stellen
                        api_cleanup_first_url = f"http://127.0.0.1/api/change/{event_id}?title=&cue=&duration=600&skip=false&timerType=clock"
                        cleanup_response = requests.get(api_cleanup_first_url)
                        print(cleanup_response)

                        time.sleep(0.5) 

                        ## Event 1 laden
                        r = requests.get(api_load_first_url)
                        print(f"load first: {r}")

                        ## einblenden
                        requests.get(api_blackout_url_false)

                    case 7:  ### -1 Minute
                        response = requests.get(api_remove1_url)
                        print(response)
                    case 8: ### -5 Minuten
                        response = requests.get(api_remove5_url)
                        print(response)
                    case 9: ### -10 Minuten
                        response = requests.get(api_remove10_url)
                        print(response)
                    case 10: ### Timer Blinken lassen
                        response = requests.get(api_blink_url_true)
                        print(response)
                    case 11: ### Timer blinken ausschalten
                        response = requests.get(api_blink_url_false)
                        print(response)
                    case 12: ### Timer ausblenden
                        response = requests.get(api_blackout_url_true)
                        print(response)
                    case 13: ### Timer anzeigen
                        response = requests.get(api_blackout_url_false)
                        print(response)
            case False:
                    print("false")
    except:
        print("An exception occurred") 

    # Don't try to draw an image on a touch button
    if key >= deck.key_count():
        return

    # Update the key image based on the new key state.
    update_key_image(deck, key, state)
    
    # Check if the key is changing to the pressed state.
    if state:
        key_style = get_key_style(deck, key, state)

        # When an exit button is pressed, close the application.
        if key_style["name"] == "exit":
            # Use a scoped-with on the deck to ensure we're the only thread
            # using it right now.
            with deck:
                # Reset deck, clearing all button images.
                deck.reset()

                # Close deck handle, terminating internal worker threads.
                deck.close()


if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):
        # This example only works with devices that have screens.
        if not deck.is_visual():
            continue

        deck.open()
        deck.reset()

        print("Opened '{}' device (serial number: '{}', fw: '{}')".format(
            deck.deck_type(), deck.get_serial_number(), deck.get_firmware_version()
        ))

        # Set initial screen brightness to 30%.
        deck.set_brightness(30)

        # Set initial key images.
        for key in range(deck.key_count()):
            update_key_image(deck, key, False)

        # Register callback function for when a key state changes.
        deck.set_key_callback(key_change_callback)

        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            try:
                t.join()
            except (TransportError, RuntimeError):
                pass
