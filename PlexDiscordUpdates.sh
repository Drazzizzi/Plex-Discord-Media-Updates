#!/bin/bash

# BEGIN USER VARIABLES --------------------------------------------------

# Path to DiscordDailyUpdates.py
PlexDiscordUpdates=""
# Uptime Kuma URL to ping (Monitor Type = Push)
PingURL=""

# END USER VARIABLES ----------------------------------------------------

output=$(python3 $PlexDiscordUpdates) &&
echo $output &&
run_time=`echo $output | awk '{print $NF}' | awk 'END{ print $0 }'` &&
curl -s -m 10 --retry 5 "$PingURL$run_time" >/dev/null
