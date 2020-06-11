import lupusecio.devices
import argparse

def get_arguments():
    parser = argparse.ArgumentParser("LupusecIO: Command Line Utility")

    parser.add_argument(
        '-u', '--username',
        help='Username for Lupusec UI',
        required=True)

    parser.add_argument(
        '-p', '--password',
        help='Password for Lupusec UI',
        required=True)

    parser.add_argument(
        '-a', '--adress',
        help='Lupus panel http Lupusec adress',
        required=True)    

    return parser.parse_args()

def call():
    args = get_arguments()

    #if not args.username or not args.password or not args.ip_address:
    #        raise Exception("Please supply a username, password and ip.")

    print(args.adress)
    system = lupusecio.devices.LupusecSystem(args.username, args.password, args.adress)
    xt1 = lupusecio.devices.XT1AlarmPanel(system)
    xt1.doUpdateSensors()
    print(xt1)
    sensors = xt1.getSensors()
    for device in sensors:
        print("ID: %s, %s" %(device, sensors.get(device)))
    
def main():
    call()

if __name__ == '__main__':
    main()