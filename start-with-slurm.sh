#!/bin/bash

# 1. Buat folder khusus user di /tmp
export MUNGE_DIR="/tmp/munge_$USER"
mkdir -p -m 700 "$MUNGE_DIR"

# 2. Setup path file untuk Munge
MUNGE_KEY="/etc/munge/munge.key"
MUNGE_SOCKET="$MUNGE_DIR/munge.socket.2"
MUNGE_LOG="$MUNGE_DIR/munged.log"
MUNGE_PID="$MUNGE_DIR/munged.pid"
MUNGE_SEED="$MUNGE_DIR/munge.seed"

# 3. Jalankan Munged
echo "Starting Munge Daemon for user $USER..."
/usr/sbin/munged \
    --force \
    --key-file="$MUNGE_KEY" \
    --socket="$MUNGE_SOCKET" \
    --log-file="$MUNGE_LOG" \
    --pid-file="$MUNGE_PID" \
    --seed-file="$MUNGE_SEED"

# 4. Set Environment Variable agar Slurm tahu socket-nya
export MUNGE_SOCKET="$MUNGE_SOCKET"

# Cek status
if ! pgrep -x "munged" > /dev/null; then
    echo "ERROR: Munge gagal start!"
    # Tampilkan log kalau ada error
    if [ -f "$MUNGE_LOG" ]; then
        cat "$MUNGE_LOG"
    fi
else
    echo "Munge started successfully at $MUNGE_SOCKET"
fi

# Jalankan Command Utama (JUPYTER)
# "$@" akan diganti dengan command asli ('jupyterhub-singleuser')
exec "$@"
