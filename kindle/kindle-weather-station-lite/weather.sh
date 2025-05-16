#!/bin/sh

v=$(cat /sys/class/graphics/fb0/virtual_size | cut -d, -f1)

case "$v" in
	600)
		ver="k3"
		;;
	768)
		ver="pw1"
		;;
	*)
		ver="k3"
		;;
esac

export KINDLE_VER=$ver
export MAGICK_HOME=/mnt/us/python3
export WAND_MAGICK_LIBRARY_SUFFIX='-6.Q8'

./weather.py $1 $2
