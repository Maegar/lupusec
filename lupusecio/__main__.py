#!/usr/bin/env python3
# Copyright 2020 Paul Proske
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import lupusecio.devices
import argparse

def get_arguments():
    parser = argparse.ArgumentParser("LupusecIO: Command Line Utility")

    _add_argument(parser, '-u', '--username', 'Username for Lupusec UI')
    _add_argument(parser, '-p', '--password', 'Password for Lupusec UI')
    _add_argument(parser, '-a', '--address', 'Lupus panel http Lupusec adress')
    _add_argument(parser, '-x', '--xt-version', 'Lupus XT version 1 or 2')
    _add_action(parser, '--no-ssl-verify', 'In case of SSL connection if certificate should be verified or not')
    _add_action(parser, '--history', 'Lupus get event history')
    _add_action(parser, '--sensors', 'Lupus get sensors')
    _add_action(parser, '--alarm-panel', 'Lupus get panel status')

    return parser.parse_args()

def _add_action(parser, argument, help, required=False):
    parser.add_argument(
        argument,
        help=help,
        required=required,
        default=False,
        action='store_true')

def _add_argument(parser, argument, argument_long, help, required=True):
    parser.add_argument(
        argument, argument_long,
        help=help,
        required=required)

def call():
    args = get_arguments()

    if not args.username or not args.password or not args.address:
        raise Exception("Please supply a username, password and ip.")

    if args.xt_version not in {'1', '2'}:
        raise Exception("Only XT version 1 and 2 are supported")

    ssl_verify = not args.no_ssl_verify
    system = lupusecio.LupusecSystem(args.username, args.password, args.address, ssl_verify)

    if args.xt_version == '1':
        xt = lupusecio.devices.XT1AlarmPanel(system)
    else:
        xt = lupusecio.devices.XT2AlarmPanel(system)
    

    report_all = not (args.alarm_panel | args.history | args.sensors)

    if args.alarm_panel | report_all:
        xt.do_update_panel_cond()
        print('--- Panel conditions ---')
        print(xt)
        print('\n')
    if args.history | report_all:
        xt.do_update_history()
        print('--- History ---')
        for event in xt.get_history():
            print(event)
        print('\n')
    if args.sensors | report_all:
        xt.do_update_sensors()
        print('--- Sensors ---')
        sensors = xt.get_sensors()
        for device in sensors:
            print("ID: %s, %s" %(device, sensors.get(device)))
        print('\n')
  

def main():
    call()

if __name__ == '__main__':
    main()