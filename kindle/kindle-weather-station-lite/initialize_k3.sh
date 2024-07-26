#!/bin/sh

if [ ! -f /tmp/customized_kindle ]; then
	pidof powerd 
	if [ $? -eq 0 ]; then
    	/etc/init.d/powerd stop
    	/etc/init.d/framework stop
	fi
	touch /tmp/customized_kindle
fi