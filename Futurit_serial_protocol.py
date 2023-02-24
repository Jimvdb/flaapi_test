"""

    Protocol for sending data

    Sync1 | Sync2 | Addr | SubAddr | Count | Tag | Chk1 | CMD | Data | Chk2

    Sync1   =   $5A
    Sync2   =   $A5
    Addr    =   Slave-addressess    :   [1-240]
                Group-addresses     :   [241-250]
                Broadcast address   :   [255]
                Reserved            :   [251-254] further use [0] indication for empty values
                In case of using Group- or Bradcasting-addresses, there is no respons
    SubAddr =   See Addr
    Count   =   1 CMD-byte + number of bytes in Data-part [n = 1 - 126]
    Tag/0   =   The Tag uses the upper four bits. It has to be increased for every new telegram
                The controller always accepts incomming tag and returns the received tag in reply. The Central system
                must check if reply telegram has expected tag, otherwise the telegram is invalid
    Chk1    =   Checksum for al previous bytes
    CMD     =   Command byte: Indicates the command descripted
    Data    =   Different content
    Chk2    =   Checksum for CMD-Byte + all data bytes

    =================================================================================================================

    Protocol for receiving data

    Sync1 | Sync2 | Addr | SubAddr | Count | Tag/CMD | Status1 | Error1 | Error2 | Chk1 | CMD | Data | Chk2

    Sync1   =   $5A
    Sync2   =   $A5
    Addr    =   Slave-addressess    :   [1-240]
                Group-addresses     :   [241-250]
                Broadcast address   :   [255]
                Reserved            :   [251-254] further use [0] indication for empty values
                In case of using Group- or Bradcasting-addresses, there is no respons
    SubAddr =   See Addr
    Count   =   1 CMD-byte + number of bytes in Data-part [n = 1 - 126]
    Tag/CMD   =   The Tag uses the upper four bits. It has to be increased for every new telegram
                The controller always accepts incomming tag and returns the received tag in reply. The Central system
                must check if reply telegram has expected tag, otherwise the telegram is invalid
                FLAGS (4 LSB)
                - 0 Bit 1 Ack
                        0 Nack
                - 1 Bit 0 Basic
                        1 Extended
    Chk1    =   Checksum for al previous bytes
    CMD     =   Command byte: Indicates the command descripted
    Data    =   Different content
    Chk2    =   Checksum for CMD-Byte + all data bytes

    =================================================================================================================

    Checksum calculation

    First byte is subtracted from zero and all other bytes from the previous

    for example:
    5A A5 00 01 01 10 XX (Checksum)

    XX = 00 - 5A - A5 - 00 - 01 - 01 - 10






"""
CONST_STATUS = {
    0x01: "PICTURE_ACTIVE: This bit is set if a picture is activated." +
          "If the sign is blank, this bit is cleared" +
          "(only if the set ContentID is zero – if the sign’s brightness is set to zero any content is activated, " +
          "the bit is still active!). 0000|0001",
    0x02: "AUTODIMMING_ACTIVE: If this bit is set, automatic dimming is activated. 0000|0010",
    0x04: "RESTARTED: This bit is set if the controller was reset." +
          " It’s cleared after the first returned telegram (with respect to the changed tag). 0000|0100",
    0x08: "COMMUNICATION_TIMEOUT: This bit is set if a configured communication timeout (see sect. 4.29) " +
          "is set and there was no communication with the sign during this period of time. 0000|1000",
    0x10: "0001|0000",
    0x20: "0010|0000",
    0x40: "0100|0000",
    0x80: "IDLE: This bit is set if the controller is currently working and unavailable to process another command " +
          "(not used on the AV-2068 controller). 1000|0000"
}
CONST_ERROR_HARDWARE = {
    0x01: "0000|0001",
    0x02: "0000|0010",
    0x04: "LED_ERROR: This bit is set, if the LED-Error limit on one segment is reached or exceeded (see sect. 0)." +
          "If the number of LED-Errors is below the LED-Error limit, the sign is reported as OK." +
          "It’s only handled after an LED-test was performed." +
          "This bit is not cleared until the next successful LED-test" +
          "(manual LED-test or automatic LED-test, see 4.17, 4.24).0000|0100",
    0x08: "POWER_ERROR: The software always checks the supply-voltage - " +
          "if the measured value is out of the configured range, this error bit is set." +
          " It’s unset after the next received telegram." +
          " If the error is still active, the bit is automatically set again. 0000|1000",
    0x10: "INTERNAL_COM_ERROR: This bit is set if any error occurred in the internal communication facilities " +
          "(i.e. communication to the LED modules). The software always checks the communication to the LED-modules." +
          "If an error is detected, this bit is set. It’s unset after the next received telegram." +
          " If the error is still active, the bit is automatically set again. 0001|0000",
    0x20: "0010|0000",
    0x40: "0100|0000",
    0x80: "CLIMATE_ERROR: This bit is set if the controller’s temperature is out of the configured range." +
          " It’s unset after the next received telegram." +
          " If the error is still active, the bit is automatically set again. 1000|0000"
}
CONST_ERROR_SOFTWARE = {
    0x01: "OUT_OF_RANGE_ERROR: This bit is set if the received parameters are out of range. 0000|0001",
    0x02: "MEMORY_ERROR: This bit is set if there is an internal error with the file system. 0000|0010",
    0x04: "CID_ERROR: If the received ContentID references an unknown ContentID, this bit is set. 0000|0100",
    0x08: "0000|1000",
    0x10: "SEQUENCE_ERROR: I.e. upload / download sequence not started properly, " +
          "wrong number of bytes in last upload-packet. 0001|0000",
    0x20: "DATA_FORMAT_ERROR:" +
          "This bit is set if the received data-format-flag is not valid for the received ContentID." +
          " 0010|0000",
    0x40: "INTERNAL_ERROR: All failures or misbehavior caused by internal functionality. 0100|0000",
    0x80: "1000|0000"
}


def two_digit_subtract(digit1, digit2):
    """
    2 getallen van elkaar aftrekken waar de max waarde 0xFF is en de min waarde 0x00
    als 0x00 -1 = 0xFF
    Voor het creëeren van de checksum
    :param digit1:
    :param digit2:
    :return:
    """
    # if digit1 == 0:
    #     digit1 == 256
    if (digit1 - digit2) < 0:
        result = digit1 - digit2 + 256
    else:
        result = digit1 - digit2

    return result


def checksum_adress_send_bytes(sync1, sync2, addr, subaddr, count, tag):
    """
    Maken van de checksum bij verzenden van data
    :param sync1:
    :param sync2:
    :param addr:
    :param subaddr:
    :param count:
    :param tag:
    :return:
    """
    checksum = two_digit_subtract(0, sync1)
    # print(f"{checksum} {hex(checksum)}")
    checksum = two_digit_subtract(checksum, sync2)
    # print(f"{checksum} {hex(checksum)}")
    checksum = two_digit_subtract(checksum, addr)
    # print(f"{checksum} {hex(checksum)}")
    checksum = two_digit_subtract(checksum, subaddr)
    # print(f"{checksum} {hex(checksum)}")
    checksum = two_digit_subtract(checksum, count)
    # print(f"{checksum} {hex(checksum)}")
    checksum = two_digit_subtract(checksum, tag)
    # print(f"{checksum} {hex(checksum)}")
    return checksum


def checksum_adress_receive_bytes(sync1, sync2, addr, subaddr, count, tag, status1, error1, error2):
    """
    Controle van de checksum bij het ontvangen van gegevens.
    Deel van de checksum berekening wordt gedaan door de send versie daar deze een identieke werking hebben.
    :param sync1:
    :param sync2:
    :param addr:
    :param subaddr:
    :param count:
    :param tag:
    :param status1:
    :param error1:
    :param error2:
    :return:
    """
    checksum = checksum_adress_send_bytes(sync1, sync2, addr, subaddr, count, tag)
    # print(f"{checksum} {hex(checksum)}")
    checksum = two_digit_subtract(checksum, status1)
    # print(f"{checksum} {hex(checksum)}")
    checksum = two_digit_subtract(checksum, error1)
    # print(f"{checksum} {hex(checksum)}")
    checksum = two_digit_subtract(checksum, error2)
    # print(f"{checksum} {hex(checksum)}")
    return checksum


def checksum_data_bytes(data):
    #   print("debug checksum_data_bytes")
    checksum = 0
    #   print(f"checksum: {checksum} data: {data}")
    for single_data in data:
        checksum = two_digit_subtract(checksum, single_data)
    #   print(f"checksum: {checksum}")
    return checksum


def calc_count(data):
    """
    :param: data: only the data is added to this request. The CMD count as 1
    :return: 1 CMD-byte + number of bytes in the DATA part (n = 1 - 126)
    """
    count = 1 + len(data)    # aanpassen naar CMD en DATA in data
    return count


def calc_count_cmd(data):
    """
    :param: data: Data and CMD byte combined
    :return: 1 CMD-byte + number of bytes in the DATA part (n= 1 - 126)
    """
    count = len(data)
    return count


def check_status_code(status_code):
    respons = "unknown"
    for status in CONST_STATUS:
        if status == status_code:
            print(hex(status))
            respons = CONST_STATUS[status_code]
    return respons


def check_error1_code(status_code):
    respons = "unknown"
    for status in CONST_ERROR_HARDWARE:
        if status == status_code:
            print(hex(status))
            respons = CONST_STATUS[status_code]
    return respons


def check_error2_code(status_code):
    respons = "unknown"
    for status in CONST_ERROR_SOFTWARE:
        if status == status_code:
            print(hex(status))
            respons = CONST_STATUS[status_code]
    return respons


def bytes_to_sendsync1(sync1, sync2, addr, subaddr, command, data):
    """
    Combineren van de nodige bits en bytes tot een list met bytes voor door te sturen naar het bord
    parameters meegegeven zijn de gewenste gegevens voor een specifiek bord aan te spreken
    :param: sync1   =   eerste synchronisatiebyte 0x5A
    :param: sync2   =   tweede synchronisatiebyte 0xA5
    :param: addr    =   addres van de controller
    :param: subaddr =   subaddres van de controller
    :param: cmd     =   command
    :param: data    =   list met data  LET OP als deze leeg is vervalt data in de return list
    :return: list [sync1, sync2, addres, subaddres, count, tag, checksum1, command, data, checksum2]
    """
    tag = 0x10      # Dit moeten nog nagekeken worden hoe we dit kunnen organiseren vermoedelijk moeten we voor een
    # een class object aanmaken om dit bij te kunnen deze moet ook optellen
    chksum2 = tag
    if len(data) == 0:
        data_count = [command]
    else:
        data_count = [command]
        for data_byte in data:
            data_count.append(data_byte)

    print(data_count)

    count = calc_count_cmd(data_count)
    var_bytes_to_send = [hex(sync1), hex(sync2), hex(addr), hex(subaddr), hex(count), hex(tag),
                         hex(checksum_adress_send_bytes(sync1, sync2, addr, subaddr, count, tag)), hex(command)]

    # toevoegen van de list met data als deze aanwezig is

    if len(data) != 0:
        for data_byte in data:
            var_bytes_to_send.append(hex(data_byte))

    # Na het toevoegen van de data checksum 2 toevoegen

    var_bytes_to_send.append(hex(checksum_data_bytes(data_count)))

    return var_bytes_to_send


def bytes_to_sendsync2(sync1, sync2, addr, subaddr, tag, command, data):
    """
    :param: data    =   list met data  LET OP als deze leeg is vervalt data in de return list
    :return: list [sync1, sync2, addres, subaddres, count, tag, checksum1, command, data, checksum2]
    """

    if len(data) == 0:
        data_count = [command]
    else:
        data_count = [command]
        for data_byte in data:
            data_count.append(data_byte)

    # print(data_count)

    count = calc_count_cmd(data_count)
    var_bytes_to_send = [hex(sync1), hex(sync2), hex(addr), hex(subaddr), hex(count), hex(tag),
                         hex(checksum_adress_send_bytes(sync1, sync2, addr, subaddr, count, tag)), hex(command)]

    # toevoegen van de list met data als deze aanwezig is

    if len(data) != 0:
        for data_byte in data:
            var_bytes_to_send.append(hex(data_byte))

    # Na het toevoegen van de data checksum 2 toevoegen

    var_bytes_to_send.append(hex(checksum_data_bytes(data_count)))

    return var_bytes_to_send
