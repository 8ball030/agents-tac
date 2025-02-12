#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This script waits until the OEF is up and running."""

import argparse
import asyncio

import oef.agents

parser = argparse.ArgumentParser("oef_healthcheck", description=__doc__)
parser.add_argument("addr", type=str, help="IP address of the OEF node.")
parser.add_argument("port", type=int, help="Port of the OEF node.")

if __name__ == '__main__':
    try:
        args = parser.parse_args()
        host = args.addr
        port = args.port
        pbk = 'check'
        print("Connecting to {}:{}".format(host, port))
        agent = oef.agents.OEFAgent(pbk, host, port, loop=asyncio.get_event_loop())
        agent.connect()
        agent.disconnect()
        print("OK!")
        exit(0)
    except Exception as e:
        print(str(e))
        exit(1)
