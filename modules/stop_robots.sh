#!/bin/bash
ps -ef | grep "robot_trader.py" | awk '{print $2 }' | xargs sudo kill
