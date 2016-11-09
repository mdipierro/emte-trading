#!/bin/bash
ps -ef | grep "matchingserver.py\|robot_trader.py" | awk '{print $2 }' | xargs sudo kill
