from picamera import PiCamera
from time import sleep
from Hologram.HologramCloud import HologramCloud
import datetime
import time
import base64
import os
import shutil

count = 0
hour = 3600
morning = False
first_try = True

while True:
    if first_try:
        timestamp = str(int(time.time()))
        log_path = "/home/pi/codebase/nova_log.txt"
        new_path = "/home/pi/codebase/logs/%s.txt" % (timestamp)

        if os.path.exists(log_path):
            shutil.copy(log_path, new_path)

        open(log_path, 'w').close()

        first_try = False
        start_time = int(time.time())

    try:
        del(hologram)
    except:
        hologram = HologramCloud(dict(), network='cellular')
    else:
        hologram = HologramCloud(dict(), network='cellular')

    modem_disconnect = hologram.network.modem.disconnect()
    network_disconnect = hologram.network.disconnect()

    print "DISCONNECTIONS => Network: " + str(network_disconnect) + " Modem: " + str(modem_disconnect)

    sleep(5)

    hologram.network.modem.disconnect()
    hologram.network.disconnect()

    sleep(5)

    try:
        del(result)
    except:
        result = hologram.network.connect()
    else:
        result = hologram.network.connect()

    if result == False:
        print ' Failed to connect to cell network. Try number %s' % (str(count + 1))
        if count > 4:
            sleep(5)

            hologram.network.modem.disconnect()
            hologram.network.disconnect()

            sleep(5)

            end_time = int(time.time())

            if morning:
                morning = False
                sleep_array = range(1, 8)
            else:
                morning = True
                sleep_array = range(1, 18)

            count = 0
            first_try = True
            run_time = end_time - start_time

            for sleep_hour in sleep_array:
                print "Sleep hour %s" % str(sleep_hour)
                if sleep_hour == 1:
                    sleep_time = hour - run_time
                    sleep(sleep_time)
                else:
                    sleep(hour)

            continue
        else:
            count += 1

            sleep(20)
            continue
    else:
        camera = PiCamera()
        date = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        image_title = "image_" + date + ".jpg"
        image_path = "/home/pi/codebase/images/" + image_title

        camera.start_preview()
        sleep(4)
        camera.capture(image_path)
        camera.stop_preview()

        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(open(image_path,"rb").read())

        character_count = len(encoded_string)
        chars_divided = character_count / 5000
        num_of_messages = chars_divided + 1
        integer = (int(num_of_messages) + 1)
        timestamp = str(int(time.time()))
        divider = "_DIVIDER_"

        print "%s characters in %s messages" % (str(character_count),str(num_of_messages))

        for n in range(1,integer):
            start_char = ((n - 1) * 5000)
            end_char = (n * 5000)
            section_of_image = encoded_string[start_char:end_char]
            message = "".join([
                "stamp", divider, timestamp, divider,
                "cluster_order", divider, str(n), divider,
                "number_of_fragments", divider, str(num_of_messages), divider,
                "total_character_count", divider, str(character_count), divider,
                "content", divider, section_of_image
            ])
            print "Sending message %d" % (n)
            response_code = hologram.sendMessage(message, topics = ["pi-one"])
            print hologram.getResultString(response_code)
            sleep(2)

        final_modem_disconnect = hologram.network.modem.disconnect()
        final_network_disconnect = hologram.network.disconnect()

        print "FINAL DISCONNECTIONS => Network: " + str(final_network_disconnect) + " Modem: " + str(final_modem_disconnect)

        if os.path.exists(image_path):
            os.remove(image_path)
        else:
            print(image_title + " does not exist.")

        end_time = int(time.time())

        if morning:
            morning = False
            sleep_array = range(1, 8)
        else:
            morning = True
            sleep_array = range(1, 18)

        count = 0
        first_try = True
        run_time = end_time - start_time

        for sleep_hour in sleep_array:
            print "Sleep hour %s" % (str(sleep_hour))
            if sleep_hour == 1:
                sleep_time = hour - run_time
                sleep(sleep_time)
            else:
                sleep(hour)

        continue
