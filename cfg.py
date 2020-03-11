from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import BoardInfo, DigitalInfo, FirmwareVersionType
from mcculw.enums import CounterInfo, ExpansionInfo, InfoType
from console import util
from props.counter import CounterProps
from mcculw.ul import ULError
from time import sleep

def run_example():

    num_ad_found = 0
    num_da_found = 0
    num_ctr_found = 0
    num_dio_found = 0
    num_tc_found = 0

    util.clear_screen()
    board_num = 0
    use_device_detection = True
    response = input('\nUse Instacal? (default n): ') or 'n'
    if response == 'y':
        use_device_detection = False

    util.clear_screen()
    if use_device_detection:
        ul.ignore_instacal()
        devices = util.detect_devices()
        if len(devices) == 0:
            print("Could not find device.")
            return
        try:
            board_num = int(input('\nEnter device number (default 0): ') or '0')
            # Add the device to the UL.
            device = devices[board_num]
            ul.create_daq_device(board_num, device)
            prod_name = device.product_name
            prod_id = device.unique_id
        except ULError as e:
            util.print_ul_error(e)
            return
    else:
        try:
            board_list = util.get_installed_boards()
            def_board = str(board_list[0])
            print('Board numbers of boards installed with Instacal: ' +
                  str(board_list))
            board_num = int(input('\nEnter device number (default ' +
                                  def_board + '): ') or def_board)
            prod_name = ul.get_board_name(board_num)
            info_type = InfoType.BOARDINFO
            config_item = BoardInfo.DEVUNIQUEID
            max_config_len = 32
            prod_id = ul.get_config_string(info_type, board_num, 0, config_item, max_config_len)
        except ULError as e:
            util.print_ul_error(e)
            return
    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id + ")\n")

    show_board_info = input('Show board info (default y)? ') or 'y'
    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id + ")\n")
    if show_board_info == 'y':
        cfg_len = 24
        index = 0

        obs_items = {BoardInfo.INITIALIZED, BoardInfo.PARENTBOARD, DigitalInfo.BASEADR,
        DigitalInfo.INITIALIZED, DigitalInfo.MASK, DigitalInfo.READWRITE,
        CounterInfo.BASEADR, CounterInfo.INITIALIZED, CounterInfo.CONFIGBYTE, BoardInfo.NOITEM}

        undoc_items = {BoardInfo.ACCOUPLED, BoardInfo.BOARDTEMP, BoardInfo.RELAYLOGIC,
        BoardInfo.OPENRELAYLEVEL, BoardInfo.DEFAULTIP, BoardInfo.CURRENTIP,
        BoardInfo.DHCPENABLED, BoardInfo.CURRENTPORT, BoardInfo.TEMPSENSORTYPE,
        BoardInfo.TEMPCONNECTIONTYPE, BoardInfo.TEMPEXCITATION, BoardInfo.TEMPCHANGAIN,
        BoardInfo.OWNERNAME, BoardInfo.OWNERIP, BoardInfo.TBASERES, BoardInfo.TEMPCALIBRATE,
        BoardInfo.CURRENTGATEWAYIP, BoardInfo.DEFAULTGATEWAYIP, BoardInfo.CURRENTSUBNET,
        BoardInfo.DEFAULTSUBNET, BoardInfo.NETMINPORT, BoardInfo.ADCPACEROUT, BoardInfo.DACPACEROUT,
        BoardInfo.BUSNUM, BoardInfo.POWERLEVEL, BoardInfo.PROGRAMDEV, BoardInfo.RFCHANENERGY,
        BoardInfo.ADCCALIBRATE, BoardInfo.ADCCALSTEPS, BoardInfo.TEMPCALSTEPS, BoardInfo.ADCSETTLETIME,
        BoardInfo.WEBSERVERENABLE, BoardInfo.ACTUALDAQSCANRATE, BoardInfo.USBQUERY, BoardInfo.DACXFERPRIMECOUNT,
        BoardInfo.EXTPOWERSTATE, BoardInfo.CHANBWMODE, BoardInfo.CALDACVREF, BoardInfo.DACCALVOLT,
        BoardInfo.USERADCSETTLETIME, BoardInfo.TERMINALCOUNTSTATUSENABLE, BoardInfo.ATRIGCALIBRATE,
        BoardInfo.ADEXCITATION, BoardInfo.ADBRIDGETYPE, BoardInfo.CALTIMEOUT, BoardInfo.ADLOADCALCOEFS,
        BoardInfo.DACLOADCALCOEFS, BoardInfo.CLOCKTIME, BoardInfo.BUTTONSTATE, BoardInfo.INTERFACEPATH,
        BoardInfo.DACCALIBRATE, BoardInfo.ATRIGRANGE, BoardInfo.LEDPATTERN, BoardInfo.ADCAVGCOUNT,
        BoardInfo.DEVINST, BoardInfo.DIFILTERTIME, BoardInfo.DISTATERETENTION, BoardInfo.HASEXTINFO,
        BoardInfo.NUMIODEVS, BoardInfo.IODEVTYPE, BoardInfo.ADNUMCHANMODES, BoardInfo.ADCHANMODE,
        BoardInfo.ADNUMDIFFRANGES, BoardInfo.ADDIFFRANGE, BoardInfo.ADNUMSERANGES, BoardInfo.ADSERANGE,
        BoardInfo.ADNUMTRIGTYPES, BoardInfo.ADTRIGTYPE, BoardInfo.ADMAXRATE, BoardInfo.ADMAXTHROUGHPUT,
        BoardInfo.ADMAXBURSTRATE, BoardInfo.ADMAXBURSTTHROUGHPUT, BoardInfo.ADHASPACER, BoardInfo.ADCHANTYPES,
        BoardInfo.ADSCANOPTIONS, BoardInfo.ADMAXSEQUEUELENGTH, BoardInfo.ADMAXDIFFQUEUELENGTH,
        BoardInfo.ADQUEUETYPES, BoardInfo.ADQUEUELIMITS, BoardInfo.DACHASPACER, BoardInfo.DACSCANOPTIONS,
        BoardInfo.DACFIFOSIZE, BoardInfo.DACNUMRANGES, BoardInfo.DACDEVRANGE, BoardInfo.DACNUMTRIGTYPES,
        BoardInfo.DACTRIGTYPE, BoardInfo.DAQAMISUPPORTED, BoardInfo.DISCONNECT, BoardInfo.CONNECTED,
        BoardInfo.NETBIOSNAME, BoardInfo.DISCANOPTIONS, BoardInfo.DOSCANOPTIONS, BoardInfo.CTRSCANOPTIONS,
        BoardInfo.DAQISCANOPTIONS, BoardInfo.DAQOSCANOPTIONS, BoardInfo.DEVCLASS, BoardInfo.DEVIPADDR,
        BoardInfo.DACDISABLERESTORE, BoardInfo.DAQINUMCHANTYPES, BoardInfo.DAQICHANTYPE, BoardInfo.DAQONUMCHANTYPES,
        BoardInfo.DAQOCHANTYPE}
        for cfg_item in BoardInfo:
            try:
                if cfg_item in obs_items:
                    continue
                if cfg_item in undoc_items:
                    continue
                cfg_len = 128
                print("{:<28}".format(cfg_item.name), end='')
                if cfg_item == BoardInfo.ADFIFOSIZE:
                    # crashes for some boards (WI 986976)
                    print('\t\tSkipped due to WI 986976')
                    continue
                switcher = {
                    BoardInfo.MFGSERIALNUM: True,
                    BoardInfo.NODEID: True,
                    BoardInfo.DEVNOTES: True,
                    BoardInfo.FACTORYID: True,
                    BoardInfo.INTERFACEPATH: True,
                    BoardInfo.DEVUNIQUEID: True,
                    BoardInfo.USERDEVID: True,
                    BoardInfo.DEVVERSION: True,
                    BoardInfo.DEVSERIALNUM: True,
                    BoardInfo.DEVMACADDR: True,
                    BoardInfo.DEVIPADDR: True
                }
                string_func = switcher.get(cfg_item, False)
                if string_func:
                    if cfg_item == BoardInfo.DEVVERSION:
                        print()
                        for dev_num in FirmwareVersionType:
                            cfg_val = ul.get_config_string(InfoType.BOARDINFO, board_num, dev_num, cfg_item, cfg_len)
                            print('   ' + "{:<25}".format(dev_num.name) + '\"' + str(cfg_val) + '\"')
                    else:
                        cfg_val = ul.get_config_string(InfoType.BOARDINFO, board_num, 0, cfg_item, cfg_len)
                        print('\"' + str(cfg_val) + '\"')
                else:
                    cfg_val = ul.get_config(InfoType.BOARDINFO, board_num, 0, cfg_item)
                    print(str(cfg_val))
                if index == 25:
                    index = 0
                    input("\nPress any key...")
                    util.clear_screen()
                    print("Device " + str(board_num) + " selected: " +
                          prod_name + " (" + prod_id + ")\n")
                index += 1
                if cfg_item == BoardInfo.NUMADCHANS:
                    num_ad_found = cfg_val
                if cfg_item == BoardInfo.NUMDACHANS:
                    num_da_found = cfg_val
                if cfg_item == BoardInfo.CINUMDEVS:
                    num_ctr_found = cfg_val
                if cfg_item == BoardInfo.DINUMDEVS:
                    num_dio_found = cfg_val
                #num_tc_found = cfg_val
            except ULError as e:
                print('\t\t\t' + e.message)
                if index == 25:
                    index = 0
                    input("\nPress any key...")
                    util.clear_screen()
                    print("Device " + str(board_num) + " selected: " +
                          prod_name + " (" + prod_id + ")\n")
                index += 1

        input('\n\nBoardInfo listing complete...')

    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id + ")\n")
    index = 0
    for cfg_item in DigitalInfo:
        try:
            print("{:<28}".format(cfg_item.name), end='')
            cfg_val = ul.get_config(InfoType.DIGITALINFO, board_num, 0, cfg_item)
            print(str(cfg_val))
            if index == 25:
                index = 0
                input("\nPress any key...")
                util.clear_screen()
                print("Device " + str(board_num) + " selected: " +
                      prod_name + " (" + prod_id + ")\n")
            index += 1
        except ULError as e:
            print('\t\t' + e.message)
            if index == 25:
                index = 0
                input("\nPress any key...")
                util.clear_screen()
                print("Device " + str(board_num) + " selected: " +
                      prod_name + " (" + prod_id + ")\n")
            index += 1

    input('\n\nDigitalInfo listing complete...')

    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id + ")\n")
    index = 0
    for cfg_item in CounterInfo:
        try:
            print("{:<28}".format(cfg_item.name), end='')
            cfg_val = ul.get_config(InfoType.COUNTERINFO, board_num, 0, cfg_item)
            print(str(cfg_val))
            if index == 25:
                index = 0
                input("\nPress any key...")
                util.clear_screen()
                print("Device " + str(board_num) + " selected: " +
                      prod_name + " (" + prod_id + ")\n")
            index += 1
        except ULError as e:
            print('\t\t' + e.message)
            if index == 25:
                index = 0
                input("\nPress any key...")
                util.clear_screen()
                print("Device " + str(board_num) + " selected: " +
                      prod_name + " (" + prod_id + ")\n")
            index += 1

    input('\n\nCounterInfo listing complete...')

    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id + ")\n")
    index = 0
    for cfg_item in ExpansionInfo:
        try:
            print("{:<28}".format(cfg_item.name), end='')
            cfg_val = ul.get_config(InfoType.EXPANSIONINFO, board_num, 0, cfg_item)
            print(str(cfg_val))
            if index == 25:
                index = 0
                input("\nPress any key...")
                util.clear_screen()
                print("Device " + str(board_num) + " selected: " +
                      prod_name + " (" + prod_id + ")\n")
            index += 1
        except ULError as e:
            print('\t\t' + e.message)
            if index == 25:
                index = 0
                input("\nPress any key...")
                util.clear_screen()
                print("Device " + str(board_num) + " selected: " +
                      prod_name + " (" + prod_id + ")\n")
            index += 1

    input('\n\nExpansionInfo listing complete...')

    util.clear_screen()

    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id+ ")\n\n")
    print('\tNumber of A/D channel\'s found:  ' + str(num_ad_found))
    print('\tNumber of D/A channel\'s found:  ' + str(num_da_found))
    print('\tNumber of Ctr channel\'s found:  ' + str(num_ctr_found))
    print('\tNumber of DIO port\'s found:  ' + str(num_dio_found))

    input('\n\nPrint channel properties?')

    if use_device_detection:
        ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()