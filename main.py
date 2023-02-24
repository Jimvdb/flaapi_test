from importlib.resources import contents

from Futurit_serial_protocol import *
import serial
import time
import sys
import glob

DEBUG = True
sync1 = 0x5A    # A6
sync2 = 0xA5    # 01
addr = ''  # 0x15     # 0x79 =121
subAddr = 0x00
# count = 0x01
tag = 0x10
# chk1
cmd = 0x37
data = []   # Bij GET-commando te gebruiken
# data = [0x16, 0x05, 0x0c, 0x0e, 0x28, 0x00]
# chk2

#   error1 = 0x09
#   error2 = 0xF7
sent_telegram = []
received_telegram = []
defecte_leds = []
compoort = ''  # 'COM5'
mogelijke_beelden = []
ser = serial.Serial()
f4a = [6, 6, 6, 6, 6, 6,
       5, 5, 5, 5, 5, 5,
       4, 4, 4, 4, 4, 4, '0', 4, 4, 4, 4, 4, 4, 4,
       3, 3, 3, 3, '0', 3, 3, 3, 3, 3, 3, 3,
       2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
       1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
       7, 7,
       8, 8]

f4b = [6,  6,  6,  6,  6,  6,  6,  6,  6,  6,
       5,  5,  5,  5,  5,  5,
       4,  4,  4,  4,  4,  4,  4,  4, 0,  4,  4,  4,  4,  4,  4,  4,
       3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,
       2,  2,  2,  2,  2,  2,  2,  2,  2,  2,
       1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1]

def init_serial():
    seri = serial.Serial()
    seri.port = compoort
    seri.timeout = 20
    seri.baudrate = 9600
    seri.open()
    print(f"Seriele poort toestand: {seri.isOpen()}")
    return seri


def methode(send_data):
    global sent_telegram
    global received_telegram
    global tag
    # log(print(f"data to send: {send_data} and type off {type(send_data)}"))

    data_to_send = []
    for info in send_data:
        data_to_send.append(int(info, 16))
    sent_telegram = data_to_send
    #   result = bytes([int(x, 16) for x in send_data])
    #   print(f"result: {result}")
    # print(f"Data to send: {data_to_send}")
    # for item in data_to_send:
    #     print(hex(item), end =" ")
    # print()
    #   print(f"Seriele poort toestand: {ser.isOpen()}")

    ser.write(bytes(data_to_send))

    log("going to read")
    bytes_to_read = 0
    while bytes_to_read == 0:
        if ser.in_waiting > 0:
            time.sleep(0.1)
            bytes_to_read = ser.in_waiting
    bytes_int = ser.read(bytes_to_read)
    types = ["sync1", "sync2", "addr", "subAddr", "count", "tag/flag", "status1", "error1", "error2", "chk1", "cmd ", "data", "chk2"]
    a = 0
    received_telegram = []
    log("\t\tint\t\thex")
    for c in bytes_int:
        log(str(a) + types[a] + "\t\t" + str(c) + "\t\t" + str(hex(c)))
        received_telegram.append(c)
        if a < len(types)-2:
            a = a+1

    log("sent_telegram: \t\t" + str(sent_telegram) + "\t\t\t\t" + ', '.join([hex(i) for i in sent_telegram]))
    log("received_telegram: \t" + str(received_telegram) + "\t" + ', '.join([hex(i) for i in received_telegram]))
    log("Done\n\n")
    if tag >= 0xF0:
        tag = tag - 0xF0
    else:
        tag = tag + 0x10
    return


def get_status():
    print("get_status")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x01, []))
    return


def set_slave_address(nieuw_address):
    global addr
    print("set_slave_address")
    methode(bytes_to_sendsync2(sync1, sync2, addr, 0x00, tag, 0x02, [nieuw_address]))
    addr = nieuw_address
    return


def get_slave_address():
    print("get_slave_address")
    methode(bytes_to_sendsync2(sync1, sync2, 0xFF, 0x00, tag, 0x03, []))
    return


def set_group_address(arg0, arg1=0, arg2=0, arg3=0, arg4=0, arg5=0, arg6=0, arg7=0, arg8=0, arg9=0):
    print("set_group_address")
    args = [arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9]
    print("Nog te configureren /t meegegeven argumenten: " + str(arg0) + ", " + str(arg1) + ", ....")
    return


def get_group_address():
    print("get_group_address")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x05, []))
    return


def set_brightness(brightness_pct):
    print("set_brightness")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x06, [brightness_pct]))
    return


def get_brightness():
    print("get_brightness")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x07, []))
    return


def set_date_time(jaar=22, dag=1, maand=1, uur=0, minuut=0, seconde=0):
    print("set_date_time")
    args = [jaar, dag, maand, uur, minuut, seconde]
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x08, args))
    return


def get_date_time():
    print("get_date_time")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x09, []))
    return


def get_software_version():
    print("get_software_version")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x0B, []))
    return


def set_digital_output(do_int: int):
    print("set_digital_output")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x0C, [do_int]))
    return


def get_category_values(category: int):
    print("get_category_values")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x0D, [category]))
    return


def get_wig_wag_parameters():
    print("get_wig_wag_parameters")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x10, []))
    return


def get_controller_id():
    print("get_controller_id")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x11, []))
    return


def reset_controller():
    print("reset_controller")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x12, []))
    return


def activate_content(content_id_msb, content_id_lsb):
    #ASYNC-COMMAND
    print("activate_content")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x1C, [content_id_msb, content_id_lsb]))
    return


def preform_led_test():
    #ASYNC-COMMAND
    print("preform_led_test")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x1D, []))
    return


def set_wig_wag_time(ontimex100ms, offtimex100ms):
    print("set_wig_wag_time")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x1E, [ontimex100ms, offtimex100ms]))
    return


def set_wig_wag_mode(mode0or1: int):
    print("set_wig_wag_mode")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x20, [mode0or1]))
    return


def sync_wig_wag():
    print("sync_wig_wag")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x21, []))
    return


def activate_dormant_content_id():
    # ASYNC-COMMAND
    print("activate_dormant_content_id")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x23, []))
    return


def set_dormant_content_id(dormandcontentid_msb, dormandcontentid_lsb):
    print("set_dormant_content_id")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x24, [dormandcontentid_msb, dormandcontentid_lsb]))
    return


def get_ledtest_timer():
    print("get_ledtest_timer")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x25, []))
    return


def set_ledtest_timer(tijd_msb, tijd_lsb):
    print("set_ledtest_timer (in x10s")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x26, [tijd_msb, tijd_lsb]))
    return


def enable_auto_dimming(enable=0):
    #0->disable
    print("enable_auto_dimming")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x27, [enable]))
    return


def set_auto_dimming(min_lux_msb, min_lux_lsb, max_lux_msb, max_lux_lsb, update_time_msb, update_time_lsb, min_intensity_pct):
    #lux 0-0xFFFF
    #0.1s 2-0xFFFF
    #tijd 0-100
    print("set_auto_dimming")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x28, [min_lux_msb, min_lux_lsb, max_lux_msb, max_lux_lsb, update_time_msb, update_time_lsb, min_intensity_pct]))
    return


def get_auto_dimming():
    #lux 0-0xFFFF
    #0.1s 2-0xFFFF
    #tijd 0-100
    print("get_auto_dimming")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x29, []))
    return


def get_async_data():
    print("get_async_data")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x37, []))
    return


def set_com_timeout(timout_msb, timout_2, timout_3, timout_lsb):
    print("set_com_timeout")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x38, [timout_msb, timout_2, timout_3, timout_lsb]))
    return


def get_com_timeout():
    print("get_com_timeout")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x39, []))
    return


def get_active_content_id():
    print("get_active_content_id")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, tag, 0x3B, []))
    return


def start_download(contentID_MSB=0xFF, contentID_LSB=0x01, data_format=0x01):
    print("start_download")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, 0x90, 0x18, [contentID_MSB, contentID_LSB, data_format]))
    return


def stop_download():
    print("stop_download")
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, 0x10, 0x19, []))
    return


def get_content(seq_nummer1=0x00, seq_nummer2=0x01):
    print("get_content --> EXTENDED TELEGRAM")
    seq_nummer = [seq_nummer1, seq_nummer2]
    methode(bytes_to_sendsync2(sync1, sync2, addr, subAddr, 0x10, 0x1b, seq_nummer))
    return


def log(a):
    if DEBUG:
        print(a)
    return 0


def zoek_led_fouten():
    preform_led_test()
    time.sleep(0.5)
    get_async_data()
    if received_telegram[8] != 0 or received_telegram[7] != 0:
        print("ERR1= " + str(received_telegram[7]) + "\nERR2= " + str(received_telegram[8]))
        # return
    log("Grootte van ontvangen telegram: " + str(len(received_telegram)) + "\n")
    if received_telegram[11] + received_telegram[12] + received_telegram[13] + received_telegram[14] == 0:
        print("Geen LED-fouten")
    else:
        for x in range(1, 11):
            start_download(0xff, x)
            time.sleep(1)
            get_content(0x00, 0x00)
            log(received_telegram)
            if received_telegram[8] == 0:
                print("Segment " + str(x) + " bestaat")
                for y in range(13, len(received_telegram)-1):
                    if received_telegram[y] != 255:
                        print("ledfout in segment ", x, ", byte ", y-13, ", code ", bin(received_telegram[y]), "\n")
                        global defecte_leds
                        defecte_leds.append([x, y-13, bin(received_telegram[y])])
            else:
                print("segment ", x, " niet gevonden \n")
    print("defecte leds:")
    print(defecte_leds)
    defecten = []
    for defect in defecte_leds:
        if not defecten.__contains__(f4a[defect[1]]):
            defecten.append(f4a[defect[1]])
            print("fout in Ledpaneel " + str(f4a[defect[1]]))
    return


def serial_ports():  # online gestolen
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def zoek_en_toon_beelden():
    global mogelijke_beelden
    get_active_content_id()
    huidig_beeld = received_telegram[11] + received_telegram[12]
    time.sleep(0.1)
    for i in range(20, 49):
        activate_content(0, i)
        time.sleep(0.5)
        if received_telegram[8] == 0x04:
            log(str(i) + " niet in het geheugen")
        else:
            get_active_content_id()
            if received_telegram[12] == i:
                mogelijke_beelden.append(i)
    activate_content(0, huidig_beeld)
    print(mogelijke_beelden)
    return


def init():
    global compoort, addr, ser
    poorten = serial_ports()
    log(str(poorten))
    if compoort == '':
        if len(poorten) != 0:
            compoort = serial_ports()[0]
        else:
            print("geen COM-poort")
            exit()
    ser = init_serial()
    time.sleep(1)


    get_slave_address()
    if addr != received_telegram[11]:
        if addr == '':
            print("oud addr " + str(addr) + "\n nieuw addr: " + str(received_telegram[11]))
            addr = received_telegram[11]
        else:
            print("Verkeerd addr: " + str(addr) + "\n adres controller: " + str(received_telegram[11]))




init()
exit()
# time.sleep(0.5)
get_status()
time.sleep(0.1)
reset_controller()
time.sleep(5)
activate_content(0, 35)
time.sleep(1)
# zoek_en_toon_beelden()
# activate_content(0, 0)
# time.sleep(1)
# get_active_content_id()
# exit()
# # get_status()
# # input("Press Enter to continue...")
# time.sleep(0.1)
preform_led_test()
time.sleep(1)
# input("Press Enter to continue...")
get_async_data()

time.sleep(0.1)
start_download(0xFF, 0x01)
time.sleep(1)

get_content(0x00, 0x00)
stop_download()
get_status()
time.sleep(.5)
print("**********************************************")
zoek_led_fouten()
time.sleep(1)

# activate_content(0, 35)
#
#
# time.sleep(0.1)
# start_download(0xFF, 0x05)
# time.sleep(0.1)
# get_async_data()
# time.sleep(0.1)
# get_content(0x00, 0x01)
# stop_download()
# get_status()
#
#
# time.sleep(0.1)
# start_download(0xFF, 0x06)
# time.sleep(0.1)
# get_async_data()
# time.sleep(0.1)
# get_content(0x00, 0x01)
# stop_download()
# get_status()

# get_active_content_id()
# time.sleep(1)

# set_digital_output(0)
# print("*******\n")
# get_com_timeout()
# print("*******\n")
# get_brightness()
# print("*******\n")
# get_auto_dimming()
# print("*******\n")
# get_ledtest_timer()
# get_slave_address()
#get_software_version()
#get_brightness()
#get_group_address()
#set_slave_address(21)
#get_date_time()
#set_date_time(22, 6, 30, 8, 40, 0)
#start_download()
#time.sleep(2)
#get_async_data()
#print("get Content 0x00 0x02")
#get_content(0x00, 0x02)
#print("get Content 0x00 0x01")
#get_content(0x00, 0x01)
#print("get Content 0x00 0x00")
#get_content(0x00, 0x00)
#stop_download()
#get_status()

ser.close()
