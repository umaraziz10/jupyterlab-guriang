#!/bin/bash

CURRENT_USER=$(whoami)

export MUNGE_DIR="/var/run/munge" 

MUNGE_KEY="/tmp/munge/munge.key"

MUNGE_SOCKET="/var/run/munge/munge.socket.2"

MUNGE_LOG="/tmp/munged.log"
MUNGE_PID="/tmp/munged.pid"
MUNGE_SEED="/tmp/munge.seed"

echo "--> Starting Munge for user: $CURRENT_USER"
echo "--> Socket Location: DEFAULT ($MUNGE_SOCKET)"

/usr/sbin/munged \
    --force \
    --key-file="$MUNGE_KEY" \
    --socket="$MUNGE_SOCKET" \
    --log-file="$MUNGE_LOG" \
    --pid-file="$MUNGE_PID" \
    --seed-file="$MUNGE_SEED"

export MUNGE_SOCKET="$MUNGE_SOCKET"
export SLURM_CONF="/etc/slurm/slurm.conf"

sleep 2
if ! pgrep -x "munged" > /dev/null; then
    echo "ERROR: Munge gagal start!"
    cat "$MUNGE_LOG"
else
    echo "SUCCESS: Munge running standard."
fi

exec "$@"
