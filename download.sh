#!/bin/bash

WAIT_TIME=${WAIT_TIME:-60}

get_datetime() {
    date '+%Y-%m-%d %H:%M:%S'
}

if [ $# -lt 1 ]; then
    echo "Usage: $0 <year> [month1 month2 ...]"
    echo "Example: $0 2024 1 2 3    # Downloads bulletins for January, February and March 2024"
    exit 1
fi

year=$1
shift

if [ $# -eq 0 ]; then
    months=$(seq 1 12)
else
    months="$@"
fi

trap 'echo -e "\nDownload script stopped by user"; exit 0' INT

for month in $months; do
    current_time=$(get_datetime)
    echo "[$current_time] Running download for $year-$month..."
    docker-compose run --rm app fetch "$year" "$month"

    current_time=$(get_datetime)
    echo "[$current_time] Download completed for $year-$month. Waiting ${WAIT_TIME} seconds..."
    sleep "$WAIT_TIME"
done
