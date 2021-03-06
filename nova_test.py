from picamera import PiCamera
from time import sleep
from Hologram.HologramCloud import HologramCloud
import datetime
import time
import base64
import os
import logging

count = 0
image_sent = False

timestamp = time.time()
stamp_string = str(int(timestamp))
file_name = "logs/%s.out" % (stamp_string)

logging.basicConfig(filename=file_name,level=logging.DEBUG,filemode='w')
logger = logging.getLogger("OUTPUT")

time_string = "Time is %s" % (str(timestamp))
logger.debug(time_string)

while True:
    try:
        del(hologram)
    except:
        hologram = HologramCloud(dict(), network='cellular')
    else:
        hologram = HologramCloud(dict(), network='cellular')

    modem_disconnect = hologram.network.modem.disconnect()
    network_disconnect = hologram.network.disconnect()

    initial_disconnections_string = "INITIAL DISCONNECTIONS => Network: " + str(network_disconnect) + " Modem: " + str(modem_disconnect)
    logger.debug(initial_disconnections_string)

    sleep(5)

    if image_sent:
        break

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
        failure_to_connect_string = 'Failed to connect to cell network. Try number ' + str(count + 1)
        logger.debug(failure_to_connect_string)

        if count > 4:
            failed_to_connect = "FAILED TO CONNECT."
            logger.debug(failed_to_connect)
            break
        else:
            count += 1
            sleep(20)
            retry_to_connect = "RETRY TO CONNECT."
            logger.debug(retry_to_connect)
            continue
    else:
        camera = PiCamera()
        date = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        image_title = "image_" + date + ".jpg"
        image_path = "/home/pi/codebase/images/" + image_title

        camera.resolution = (720, 480)
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
        timestamp = int(time.time())
        divider = "_DIVIDER_"

        chars_in_msg_string = "%s characters in %s messages" % (str(character_count),str(num_of_messages))
        logger.debug(chars_in_msg_string)

        for n in range(1,integer):
            start_char = ((n - 1) * 5000)
            end_char = (n * 5000)
            section_of_image = encoded_string[start_char:end_char]
            message = "".join([
                "stamp", divider, str(timestamp), divider,
                "cluster_order", divider, str(n), divider,
                "number_of_fragments", divider, str(num_of_messages), divider,
                "total_character_count", divider, str(character_count), divider,
                "content", divider, section_of_image
            ])
            sending_msg_string = "Sending message %d" % (n)
            logger.debug(sending_msg_string)

            response_code = hologram.sendMessage(message, topics = ["pi-one"])
            hologram_result_string = hologram.getResultString(response_code)
            logger.debug(hologram_result_string)
            sleep(2)

        final_modem_disconnect = hologram.network.modem.disconnect()
        final_network_disconnect = hologram.network.disconnect()

        final_disconnections_string = "FINAL DISCONNECTIONS => Network: " + str(final_network_disconnect) + " Modem: " + str(final_modem_disconnect)
        logger.debug(final_disconnections_string)

        if os.path.exists(image_path):
            os.remove(image_path)
            file_removed_string = image_title + " removed."
            logger.debug(file_removed_string)
        else:
            no_file_string = image_title + " does not exist."
            logger.debug(no_file_string)

        image_sent = True

        time_complete_string = "COMPLETE at %s" % (str(time.time()))
        logger.debug(time_complete_string)

        break
