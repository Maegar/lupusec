import lupusecio.devices
import argparse

def get_arguments():
    parser = argparse.ArgumentParser("LupusecIO: Command Line Utility")

    _addArgument(parser, '-u', '--username', 'Username for Lupusec UI')
    _addArgument(parser, '-p', '--password', 'Password for Lupusec UI')
    _addArgument(parser, '-a', '--address', 'Lupus panel http Lupusec adress')
    _addArgument(parser, '-x', '--xt-version', 'Lupus XT version 1 or 2')
    _addAction(parser, '--history', 'Lupus get event history')
    _addAction(parser, '--sensors', 'Lupus get sensors')
    _addAction(parser, '--alarm-panel', 'Lupus get panel status')

    return parser.parse_args()

def _addAction(parser, argument, help, required=False):
    parser.add_argument(
        argument,
        help=help,
        required=required,
        default=False,
        action='store_true')

def _addArgument(parser, argument, argumentLong, help, required=True):
    parser.add_argument(
        argument, argumentLong,
        help=help,
        required=required)

def call():
    args = get_arguments()

    if not args.username or not args.password or not args.address:
        raise Exception("Please supply a username, password and ip.")

    if args.xt_version not in {'1', '2'}:
        raise Exception("Only XT version 1 and 2 are supported")

    system = lupusecio.LupusecSystem(args.username, args.password, args.address)

    if args.xt_version == '1':
        xt = lupusecio.devices.XT1AlarmPanel(system)
    else:
        xt = lupusecio.devices.XT2AlarmPanel(system)
    
    
    reportAll = True if not (args.alarm_panel & args.history & args.sensors) else False

    if args.alarm_panel | reportAll:
        xt.doUpdatePanelCond()
        print('--- Panel conditions ---')
        print(xt)
        print('\n')
    if args.history | reportAll:
        xt.doUpdateHistory()
        print('--- History ---')
        for event in xt.getHistory():
            print(event)
        print('\n')
    if args.sensors | reportAll:
        xt.doUpdateSensors()
        print('--- Sensors ---')
        sensors = xt.getSensors()
        for device in sensors:
            print("ID: %s, %s" %(device, sensors.get(device)))
        print('\n')
  

def main():
    call()

if __name__ == '__main__':
    main()