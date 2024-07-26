#!/bin/sh

if [ -f /tmp/customized_kindle ]; then
	pidof powerd 
	if [ $? -ne 0 ]; then
    	/etc/init.d/powerd start
    	/etc/init.d/framework start
	fi
	rm /tmp/customized_kindle
fi
reboot
