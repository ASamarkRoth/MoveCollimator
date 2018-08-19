#!/bin/bash

F_INPUT="surface"

./move_collimator.py -set_power_com 
./move_collimator.py -swipe_file $F_INPUT 10 50 20 10 50 20
./move_collimator.py -file_xy $F_INPUT 

echo temp.$F_INPUT.scan

#6q means the stop: ? is on the sixth line of the config file = .scan.yaml
ON="$(sed '6q;d' .scan.yaml | awk '{print $2}')"
while [ -f temp.$F_INPUT.scan ] && [ "$ON" == "0" ]; do  
	./move_collimator.py
	ON="$(sed '6q;d' .scan.yaml | awk '{print $2}')"
done

if [ "$ON" == "1" ]; then
	echo "Emergency stop activated, exiting normally!"
fi

mv stepper.log "$F_INPUT"_stepper.log
mv coords.log "$F_INPUT"_coords.log
mv power.log "$F_INPUT"_power.log

./move_collimator.py -no_file
./move_collimator.py -no_power_com 

echo "Swipe Scan completed"
