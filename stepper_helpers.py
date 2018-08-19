
""" Evaluating the steps necessary to invoke to move to the new position. 

STEPPER_Y: KK5002 has a lead of 2 mm.
STEPPER_X: KK6005 has a lead of 5 mm.

Both stepper motors 17H261-02S/D has a stepping angle: 1.8 deg (rotarystepper catalogue)
Step-accuracy: +- 0.05 deg (rotarystepper catalogue)

"""
import sys
import numpy as np
import os
import shutil

import yaml

DAQ_PWD = "/LynxOS/mbsusr/mbsdaq/mbsrun/Fl_1819_mbsdaq_unkaputt/mbs/"
SSH_ADR = " mbsdaq@lipc-1"
SSH = "ssh "

class Scanner:

    #Initialises class
    def __init__(self, config_file, dir_path):
        self.config_file = config_file
        self.dir_path = dir_path
        self.step_length_y = (1.8/360)*2
        self.step_length_x = (1.8/360)*5


    #This is invoked if a setting in the config_file is to be changed.
    def ChangeSetting(self, setting, value):
        stream = open(self.dir_path+self.config_file, 'r+')
        doc = yaml.load(stream)
        if setting in doc:
            doc[setting] = value
        else:
            print("Setting", setting, "does not exist in the configure file")
            return False
        stream.seek(0)
        stream.truncate()
        yaml.dump(doc, stream)
        stream.close()
        return True

    #Reads the setting in the config_file.
    def ReadSetting(self, setting):
        stream = open(self.dir_path+self.config_file, 'r+')
        doc = yaml.load(stream)
        if setting not in doc:
            print("Setting", setting, "does not exist in the configure file")
            return None
        stream.close()
        #print("yaml=", doc)
        return doc[setting]

    #Reads the next coordinate from the file specified by file_xy and generated by -swipe_file.
    def ReadCoordsFile(self):
        with open(self.dir_path+"temp."+self.ReadSetting("read_file")+".scan", 'r') as f:
            content = f.readlines()
            if len(content) > 0:
                return map(float, (content[0].rsplit()))
            else:
                return None, None
            

    #Calculates the new position on the basis of how many steps are taken.
    def PosEval(self, new_x, new_y):
        x, y = self.ReadSetting("pos")
        print("Current position is:", x, y)
        new_steps_y = round((new_y-float(y))/self.step_length_y)
        new_steps_x = round((new_x-float(x))/self.step_length_x)
        new_y = new_steps_y*self.step_length_y + float(y)
        new_x = new_steps_x*self.step_length_x + float(x)
        new_y = "{0:.3f}".format(round(new_y,3))
        new_x = "{0:.3f}".format(round(new_x,3))
        print("New planned position is:", new_x, new_y)
        print("Invoking step:", new_steps_x, new_steps_y)
        return new_steps_x, new_steps_y

    #Calculates the new position on the basis of how many steps that should be taken.
    def SetNewPosition(self, went_x, went_y):
        if went_x == 0 and went_y == 0:
            return
        x_old, y_old = self.ReadSetting("pos")
        new_y = went_y*self.step_length_y + float(y_old)
        new_x = went_x*self.step_length_x + float(x_old)
        new_y = "{0:.3f}".format(round(new_y,3))
        new_x = "{0:.3f}".format(round(new_x,3))
        print("New position is to be:", new_x, new_y)

    #Calculates the new position on the basis of how many steps were taken (endstops might be reached).
    def SetRealPosition(self, went_x, went_y):
        x_old, y_old = self.ReadSetting("pos")
        new_y = went_y*self.step_length_y + float(y_old)
        new_x = went_x*self.step_length_x + float(x_old)
        new_y = "{0:.3f}".format(round(new_y,3))
        new_x = "{0:.3f}".format(round(new_x,3))
        print("New real position is: ", new_x, new_y )
        self.ChangeSetting("pos", [new_x, new_y])
        with open(self.dir_path+"coords.log", 'a') as f_temp:
            f_temp.write(new_x + " " + new_y+"\n")

    #Invoked every time the collimator has moved and we are reading from file.
    def PerformedMove(self):
        #print(self.ReadSetting("read_file"))
        with open(self.dir_path+"temp."+self.ReadSetting("read_file")+".scan", 'r') as f_in:
            content = f_in.readlines()
        with open(self.dir_path+"temp."+self.ReadSetting("read_file")+".scan", 'w') as f_out:
            f_out.seek(0, 0)
            f_out.writelines(content[1:])
        #print("Removing .pause_scan @rio4-1")
        #os.system("ssh mbsdaq@rio4-1 \"rm /nfs/mbsusr/mbsdaq/mbsrun/Scanner/mbs/vme_0/.pause_scan\"")

    #Invoked when a full scan is finished.
    def Finished(self):
        self.ChangeSetting("is_file", 0)
        try:
            os.remove(self.dir_path+"temp."+self.ReadSetting("read_file")+".scan")
        except FileNotFoundError:
            print("Ops, could not remove temp file as it does not exist")
        #os.system("ssh mbsdaq@rio4-1 'rm /nfs/mbsusr/mbsdaq/mbsrun/Scanner/mbs/vme_0/.pause_scan; touch /nfs/mbsusr/mbsdaq/mbsrun/Scanner/mbs/vme_0/.finished_scan'")
        self.ForkProcCmd(SSH + SSH_ADR + " \"touch "+ DAQ_PWD + ".finished_scan\"")
        name = self.ReadSetting("read_file")
        sys_comm = SSH + SSH_ADR + " \"mkdir -p " + DAQ_PWD + "/scan/"+name+"\""
        self.ForkProcCmd(sys_comm)
        sys_comm = "scp "+self.dir_path+"stepper.log "+self.dir_path+"coords.log "+self.dir_path+"power.log "+self.dir_path+name+".scan "+SSH_ADR + ":" + DAQ_PWD + "scan/"+name+"/"
        self.ForkProcCmd(sys_comm)
        #sys_comm = "scp "+self.dir_path+"coords.log "+"mbsdaq@rio4-1:/nfs/mbsusr/mbsdaq/mbsrun/Scanner/mbs/vme_0/scan/"+name+"/"
        #os.system(sys_comm)
        #sys_comm = "scp "+self.dir_path+"power.log "+"mbsdaq@rio4-1:/nfs/mbsusr/mbsdaq/mbsrun/Scanner/mbs/vme_0/scan/"+name+"/"
        #os.system(sys_comm)

        self.ChangeSetting("is_file", 0)
        self.ChangeSetting("is_power_com", 0)
        sys.exit()

    #Communicating with the tdk power supply via the script power_set.
    def SetPower(self, s):
        print("Executing: ", self.dir_path+"power_set cmd "+s)
        os.system(self.dir_path+"power_set cmd "+s)
        os.system(s +" >> "+self.dir_path+"power.log")

    #Via the option -swipe_file the user invokes this function which creates a coordinate file to read from.
    def GenerateSwipeFile(self, s):
        x = np.arange(float(s[1]), float(s[2]) + float(s[3]), float(s[3]))
        y = np.arange(float(s[4]), float(s[5]) + float(s[6]), float(s[6]))
        print("x=",x)
        print("y=",y)
        with open(self.dir_path+s[0]+'.scan', 'w') as f:
            for j in range(len(y)):
                for i in range(len(x)):
                    if j%2 == 1: 
                        f.write(str(x[-i-1])+' '+str(y[j])+'\n')
                    else:
                        f.write(str(x[i])+' '+str(y[j])+'\n')
    
    #Calculates the time the program should sleep on the basis of the amount of steps in x & y and the frequency.
    def GetSleep(self, steps_x, steps_y):
        sleepy = 0
        FREQ = self.ReadSetting("freq")
        if abs(steps_y) > abs(steps_x):
            sleepy = abs(float(steps_y/FREQ))
        else:
            sleepy = abs(float(steps_x/FREQ))
        return sleepy

    #Calculates the number of missed steps in either x or y. Missed steps can occur when endstops are reached.
    def GetMissed(self, steps_xy, missed_xy):
        m_xy = float(missed_xy[0])
        if steps_xy < 0:
            m_xy = -float(missed_xy[0])
        return m_xy

    #If any steps are missed during a scan this is invoked which cancels all DAQ
    def AbortScan(self):
        self.ForkProcCmd(SSH + SSH_ADR + " \"touch " + DAQ_PWD + ".abort_scan\"")
        #Should send data to. Perhaps even send a notification!

    def ResetCoordFile(self, index):
        index = int(index[0])
        shutil.copyfile(self.dir_path+self.ReadSetting("read_file")+".scan", self.dir_path+"temp."+self.ReadSetting("read_file")+".scan")
        with open(self.dir_path+"temp."+self.ReadSetting("read_file")+".scan", 'r') as f_in:
            content = f_in.readlines()
        with open(self.dir_path+"temp."+self.ReadSetting("read_file")+".scan", 'w') as f_out:
            f_out.seek(0, 0)
            f_out.writelines(content[index:])

    def ForkProcCmd(self, cmd):
        pid = os.fork()
        if pid == -1:
            print("Failed to fork!")
            sys.exit(1)
        if pid == 0:
            print("Child cmd:", cmd)
            os.system(cmd)
            print("Child exiting")
            sys.exit(0)
        else:
            os.waitpid(pid, 0)
            print("Parent, done")


if __name__ == '__main__':
    dir_path = "/home/pi/Documents/ScanningSystem/atlundiumberry/"
    config_file = '.scan.yaml'
    Scan = Scanner(config_file, dir_path)
    Scan.Finished()
