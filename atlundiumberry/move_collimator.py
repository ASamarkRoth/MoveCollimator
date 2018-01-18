#!/usr/bin/python3

# DO NOT FORGET TO COPY IT!!!!!!
#sudo cp move_collimator.py /usr/local/bin/

import os
import sys
import argparse
import shutil

sys.path.insert(0, "/home/pi/Documents/ScanningSystem/atlundiumberry/")

import stepper_helpers as sh

#directory in which this file exists
#dir_path = os.path.dirname(os.path.realpath(__file__))+"/"
dir_path = "/home/pi/Documents/ScanningSystem/atlundiumberry/"
#print("Directory of program:", dir_path)

parser = argparse.ArgumentParser("Specify how many steps that should be taken in as: 'steps_x steps_y'")
parser.add_argument("-step", dest='steps', type=int, help="steps_x steps_y", nargs=2)
parser.add_argument("-new_origin", dest='new_xy', action="store_true", help="Set current position as origin.")
parser.add_argument("-xy", dest='xy', nargs=2, help="Provide the new coordinates as: 'x y' (mm)")
parser.add_argument("-swipe_file", dest='swipe', nargs=7, help="Generate a file with coordinates to perform an (x0-x1, y0-y1) with step lengths (dx, dy) swipe scan. As: 'file_name x0 x1 dx y0 y1 dy'. Neglect file ending.")
parser.add_argument("-file_xy", dest='file_xy', nargs=1, help="Provide the file name from which the position data is to be read from. If file is set then every time the program is executed the collimator will move to the positions indicated in the file. A temporary file temp.'file name'.scan is deleted if the scan is completed.")
parser.add_argument("-no_file", dest='no_file', action="store_true", help="Deactivate read from file.")
parser.add_argument("-set_freq", dest='freq', nargs=1, help="Set freq as: 'new_freq' (Hz)")
parser.add_argument("-set_defaults", dest='defs', action="store_true", help="Reset default settings.")
parser.add_argument("-set_power_com", dest='tdk', action="store_true", help="Set up the power supply communication (tdk-lambda Gen 50-30). OBS: this activates automatic power ON/OFF over the operation.")
parser.add_argument("-no_power_com", dest='no_tdk', action="store_true", help="Inactivate automatic power supply communication and power ON/OFF during operation.")
parser.add_argument("-STOP", dest='stop', action="store_true", help="Emergency stop the scanning!")
parser.add_argument("-clear_coords", dest='coords', action="store_true", help="Clear the coordinate (coords.log) file.")
parser.add_argument("-clear_log", dest='clear_log', action="store_true", help="Clear the stepper log-file.")
parser.add_argument("-clear_logs", dest='clear_logs', action="store_true", help="Clear ALL log-files.")
parser.add_argument("-ON", dest='on', action="store_true", help="Deactivate emergency stop.")
parser.add_argument("-ResetToOrigin", dest='resetO', action="store_true", help="Reset coordinates to origin, i.e. where sensors at (x0, y0) activate.")
parser.add_argument("-ResetToIndex", dest='c_index', nargs=1, help="Reset the coordinate file to the index corresponding to the desired read file @rio4-1. If power communication and reading from file is not set they will be activated. OBS, it resets to the lastly written (not finished) file.")
parser.add_argument("-v", dest='view', action="store_true", help="View current settings.")
args = parser.parse_args()

#print(args)

steps_x = 0
steps_y = 0

config_file = '.scan.yaml'
Scan = sh.Scanner(config_file, dir_path)

orig_stdout = sys.stdout

f_log = open("stepper.log", 'w')

if args.on:
    print("Deactivating emergency stop.")
    Scan.ChangeSetting("stop", 0)

if Scan.ReadSetting("stop"):
    print("EMERGENCY STOP ACTIVATED!")
    sys.exit(2)

#sys.stdout = f_log

if len(sys.argv)==1:
    #print("is_file=", Scan.ReadSetting("is_file"))
    if Scan.ReadSetting("is_file"):
        x, y = Scan.ReadCoordsFile()
        if x == None and y == None:
            Scan.Finished()
        steps_x, steps_y = Scan.PosEval(x, y)
        if steps_x == 0 and steps_y == 0:
            Scan.PerformedMove()
    else:
        parser.print_help()
        Scan.ChangeSetting("is_file", 0)
        sys.exit(1)

if args.tdk:
    print("Setting up power supply communication ")
    #os.system("echo 'Setting up tdk-lambda'")
    os.system(Scan.dir_path+"power_set setup &")
    Scan.ChangeSetting("is_power_com", 1)

if args.no_tdk:
    print("Inactivating power supply communication ")
    Scan.ChangeSetting("is_power_com", 0)

if args.view:
    print("\nCurrent settings are:")
    os.system("cat " + Scan.dir_path+Scan.config_file)
    print("")

if args.clear_log:
    print("Clearing stepper log file: \"stepper.log\"")
    os.system("cp /dev/null stepper.log")

if args.clear_logs:
    print("Clearing log files: \"stepper.log\", \"coords.log\" and \"power.log\"")
    os.system("cp /dev/null stepper.log")
    os.system("cp /dev/null coords.log")
    os.system("cp /dev/null power.log")

if args.coords:
    print("Clearing coordinate log file: \"coords.log\"")
    os.system("cp /dev/null coords.log")

if args.stop:
    print("\n Emergency stop with current settings:")
    os.system("cat " + Scan.dir_path+Scan.config_file)
    Scan.ChangeSetting("stop", 1)
    print("")
    sys.exit(2)

if args.resetO:
    steps_x, steps_y = Scan.PosEval(-1, -1)
    print("Resetting to position (0, 0)", "Stepping [x, y]: [", steps_x,", ",steps_y,"]")

if args.c_index:
    print("Resetting the coordinate file to index: ", args.c_index)
    Scan.ResetCoordFile(args.c_index)
    print("Ensuring read from file and power communication is activated ...")
    Scan.ChangeSetting("is_file", 1)
    os.system(Scan.dir_path+"power_set setup")
    Scan.ChangeSetting("is_power_com", 1)

if args.freq:
    print("Setting frequency to: ", args.freq)
    Scan.ChangeSetting("freq", args.freq)

if args.defs:
    print("Setting defaults")
    Scan.ChangeSetting("freq", 50)
    Scan.ChangeSetting("is_file", 0)
    Scan.ChangeSetting("is_power_com", 0)

if args.swipe:
    print("Generating swipe file:", args.swipe[0]+".scan")
    Scan.GenerateSwipeFile(args.swipe)

if args.new_xy: 
    Scan.ChangeSetting("pos", [0, 0]);
    print("The new origin has been successfully added to"+config_file)
    sys.exit()

if args.file_xy:
    print("Setting file to read from:", args.file_xy[0])
    Scan.ChangeSetting("is_file", 1)
    Scan.ChangeSetting("read_file", args.file_xy[0])
    os.system("> coords.log")
    os.system("> power.log")
    os.system("> stepper.log")
    shutil.copyfile(Scan.dir_path+args.file_xy[0]+".scan", Scan.dir_path+"temp."+args.file_xy[0]+".scan")

if args.no_file:
    print("Deactivating read file")
    Scan.ChangeSetting("is_file", 0)

if args.steps:
    steps_x = args.steps[0]
    steps_y = args.steps[1]
    Scan.SetNewPosition(float(steps_x), float(steps_y))

if args.xy:
    steps_x, steps_y = Scan.PosEval(float(args.xy[0]), float(args.xy[1]))
    #print("Stepping [x, y]: [", steps_x,", ",steps_y,"]")

if steps_x == 0 and steps_y == 0: 
    print("Exiting since no steps set")
    sys.exit(0)

if not Scan.ReadSetting("is_power_com"):
    print("Power communication have not been set. Doing that now...")
    os.system(Scan.dir_path+"power_set setup")
    Scan.ChangeSetting("is_power_com", 1)

print("Stepping [x, y]: [", steps_x,", ",steps_y,"]")

import time

# Use the Gertbot drivers
import gertbot as gb

# Initial settings:
BOARD = 3           # which board we talk to
# View the linear units from the where the wagons are as close as possible to the motors: Y is bottom motor (i.e. running the KK50) and X is top motor (i.e. running the KK60)
STEPPER_Y = 0       # channel for first stepper motor
STEPPER_X = 2       # channel for second stepper motor
MODE = gb.MODE_STEPG_OFF          # stepper control, gray code
# mode    0=odd
#         1=brushed
#         2=DCC
#         8=step gray off
#         9=step pulse off 
#        24=step gray powered
#        25=step pulse powered
FREQ = Scan.ReadSetting("freq")        # frequency

#print("Set frequency is:", FREQ)

# Main program

# Open serial port to talk to Gertbot
#print("Opening serial port ...")
gb.open_uart(0)

# Setup the channels for stepper motors
#print("Setting up channels for stepper motors ...")
gb.set_mode(BOARD,STEPPER_Y,MODE)
gb.freq_stepper(BOARD,STEPPER_Y,FREQ)
gb.set_mode(BOARD,STEPPER_X,MODE)
gb.freq_stepper(BOARD,STEPPER_X,FREQ)

# END-STOP NEEDS TO BE IMPLEMENTED CAREFULLY. (note motor polarisation and j3-pin!)
# ENDSTOP_OFF = 0
# ENDSTOP_LOW = 1
# ENDSTOP_HIGH = 2

# Set active-low endstop as: 
#def set_endstop (board,channel,stop_A,stop_B)

gb.set_endstop(BOARD, STEPPER_Y, gb.ENDSTOP_LOW, gb.ENDSTOP_LOW)
gb.set_endstop(BOARD, STEPPER_X, gb.ENDSTOP_LOW, gb.ENDSTOP_LOW)

sleepy = Scan.GetSleep(steps_x, steps_y)

s_out = "echo \"Invoking move. Duration: "+str(sleepy)+" s ...\""
os.system(s_out)

if Scan.ReadSetting("is_power_com"):
    print("Activating power")
    Scan.SetPower("OUT 1")
    time.sleep(2) #this is to ensure power is on

# DO THE ACTUAL MOVE
print("Invoking move ...")
gb.move_stepper(BOARD,STEPPER_Y,steps_y)
gb.move_stepper(BOARD,STEPPER_X,steps_x)

#Checking status after move for both motors and aborts if anything is wrong.
#This is somewhat unclear still
#motor_status = gb.get_motor_status(BOARD, STEPPER_Y)
#print("Motor status Y: ", motor_status) 
#if steps_y != 0 and any(motor_status) != 0:
#    print("There was a motor error/end stop reached for motor Y. - The run is aborted.")
#
#motor_status = gb.get_motor_status(BOARD, STEPPER_X)
#print("Motor status X: ", motor_status)
#if steps_x != 0 and any(motor_status) != 0:
#    print("There was a motor error/end stop reached for motor X. - The run is aborted.")

#status = gb.get_io_setup(BOARD)
#print("Status: ", status)

print("Now sleeping "+str(sleepy)+" s ...")
time.sleep(sleepy)

missed_y = gb.get_motor_missed(BOARD, STEPPER_Y)
missed_x = gb.get_motor_missed(BOARD, STEPPER_X)
m_x = Scan.GetMissed(steps_x, missed_x)
m_y = Scan.GetMissed(steps_y, missed_y)
#print("Missed X,Y: ", missed_x, missed_y)
print("Missed X,Y: ", m_x, m_y)

Scan.SetRealPosition(steps_x-m_x, steps_y-m_y)

if args.resetO:
    #Due to some error, we might not be at real (x0, y0) -> looping here till missed > 0
    while m_x == 0 or m_y == 0:
        steps_x, steps_y = Scan.PosEval(-5, -5)
        if m_x == 0:
            gb.move_stepper(BOARD,STEPPER_X,steps_x)
        if m_y == 0:
            gb.move_stepper(BOARD,STEPPER_Y,steps_y)
        sleepy = Scan.GetSleep(steps_x, steps_y)
        time.sleep(sleepy)
        if m_x == 0: 
            missed_x = gb.get_motor_missed(BOARD, STEPPER_X)
            m_x = Scan.GetMissed(steps_x, missed_x)
        if m_y == 0:
            missed_y = gb.get_motor_missed(BOARD, STEPPER_Y)
            m_y = Scan.GetMissed(steps_y, missed_y)

    print("RESETTING to (0,0)")
    Scan.ChangeSetting("pos", [0, 0])

#print("Reading error status ...")
status = gb.read_error_status(BOARD)
print("Status received ...")
if status != 0:
    print("Gertbot reports error(s):")    
    print(gb.error_string(status))
else:
    print("all good!")  

# Added this to avoid motor going into pwr state after end-stop activation.
gb.set_mode(BOARD,STEPPER_X,MODE)
gb.set_mode(BOARD,STEPPER_Y,MODE)

if Scan.ReadSetting("is_power_com"):
    print("Deactivating power")
    Scan.SetPower("OUT 0")

if Scan.ReadSetting("is_file"):
    if m_x > 0 or m_y > 0:
        Scan.ForkProcCmd("ssh mbsdaq@rio4-1 \"touch /nfs/mbsusr/mbsdaq/mbsrun/Scanner/mbs/vme_0/.abort_scan\"")
    else:
        Scan.PerformedMove()

f_log.close()
sys.stdout = orig_stdout

#Seems necessary for the ssh session to end?
sys.exit(0)

# on exit stop everything
#gb.emergency_stop()


