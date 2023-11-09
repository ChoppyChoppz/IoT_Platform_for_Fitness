"""
    GeneralUserInterface for IoT platform Fitness.
    
"""

import sys
from PyQt5 import QtWidgets
from WebClient import WebClient


class MainWindow(QtWidgets.QMainWindow):
    """ Set up interface main window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fitness")
        self.central_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.setFixedSize(800,500)
        self.start_window()

    def start_window(self):
        self.home_widget = Home(self)
        self.home_widget.addp_button.clicked.connect(self.adding_patient)
        self.home_widget.delp_button.clicked.connect(self.deleting_patient)
        self.home_widget.device_button.clicked.connect(self.devices)
        self.central_widget.addWidget(self.home_widget)
        self.central_widget.setCurrentWidget(self.home_widget)
        self.home_widget.back_button.clicked.connect(self.start_window)

    def adding_patient(self):
        self.new_patient_widget = NewPatient(self)
        self.central_widget.addWidget(self.new_patient_widget)
        self.central_widget.setCurrentWidget(self.new_patient_widget)
        self.new_patient_widget.back_button.clicked.connect(self.start_window)
        
    def deleting_patient(self):
        self.del_patient_widget = ManagePatient(self)
        self.central_widget.addWidget(self.del_patient_widget)
        self.central_widget.setCurrentWidget(self.del_patient_widget)
        self.del_patient_widget.back_button.clicked.connect(self.start_window)
        self.del_patient_widget.back_button1.clicked.connect(self.start_window)
    
    def devices(self):
        self.device_widget = ManageDevice(self)
        self.central_widget.addWidget(self.device_widget)
        self.central_widget.setCurrentWidget(self.device_widget)
        self.device_widget.back_button.clicked.connect(self.start_window)      


class Home(QtWidgets.QWidget):
    """ HOME window layout """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QtWidgets.QGridLayout(self)

        self.alarm_label = QtWidgets.QLabel("Alarm")
        self.alarm_combo = QtWidgets.QComboBox()             #dropdown menu        
        self.alarm_dict, self.alarm_dictID = WebClient().get_patients_alarm()
        for k,v in self.alarm_dict.items():        #add items to dropdown menu
            self.alarm_combo.addItem(k)
            
        self.contact_label = QtWidgets.QLabel("InfoContact") 
        namePatient = str(self.alarm_combo.currentText())
        if len(self.alarm_dict):
            self.contact_box = QtWidgets.QLineEdit(self.alarm_dict[namePatient])
            self.contact_box.setReadOnly(True)
            self.remala_button = QtWidgets.QPushButton('Remove Alarm')
            self.grid_layout.addWidget(self.remala_button,3,1,1,1)
            self.remala_button.clicked.connect(self.deletingAlarm)

        else:
            self.contact_box = QtWidgets.QLineEdit('')
            self.contact_box.setReadOnly(True)
        
        self.addp_button = QtWidgets.QPushButton('New Patient')
        self.delp_button = QtWidgets.QPushButton('Manage Patient')
        self.device_button = QtWidgets.QPushButton('Manage Device')
        self.back_button = QtWidgets.QPushButton('Back')
        
        self.grid_layout.addWidget(self.alarm_label, 1, 0)
        self.grid_layout.addWidget(self.alarm_combo, 1, 1, 1, 4)
        self.grid_layout.addWidget(self.contact_label, 2, 0)
        self.grid_layout.addWidget(self.contact_box, 2, 1, 1, 4)
        self.grid_layout.addWidget(self.addp_button,4,1,1,1)
        self.grid_layout.addWidget(self.delp_button,4,2,1,1)
        self.grid_layout.addWidget(self.device_button,4,3,1,1)

        self.alarm_combo.currentIndexChanged.connect(self.contact_drop)
        

    def contact_drop(self):
        self.contact_box.clear()
        namePatient = str(self.alarm_combo.currentText())
        self.contact_box.setText(self.alarm_dict[namePatient])  

    def deletingAlarm(self):
        ind = self.alarm_combo.currentIndex()
        params = {'patientID' : list(self.alarm_dictID.values())[ind]}
        WebClient().delete_alarm(params)  
        self.deleted_alarm()
        return 
    
    def deleted_alarm(self):
        del_alarm_label = QtWidgets.QLabel("Alarm %s deleted" %(str(self.alarm_combo.currentText())))
        for cnt in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.takeAt(cnt).widget()
            if widget is not None:
                widget.deleteLater()
            
        self.grid_layout.addWidget(del_alarm_label, 1, 0, 1, -1)
        self.grid_layout.addWidget(self.back_button,4,3,1,1)
    
        
        
class NewPatient(QtWidgets.QWidget):
    """ NEW PATIENT window layout """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QtWidgets.QGridLayout(self)

        ''' Define data to insert'''
        self.patient_label = QtWidgets.QLabel("Patient - name surname: ")  # text
        self.patient_box = QtWidgets.QLineEdit()                       # text box
        
        self.age_label = QtWidgets.QLabel("Age: ")
        self.age_box = QtWidgets.QSpinBox()
        self.age_box.setRange(0, 100)

        self.height_label = QtWidgets.QLabel("Height: ")
        self.height_box = QtWidgets.QDoubleSpinBox()
        self.height_box.setRange(0, 3)
        self.height_box.setDecimals(2)
        self.height_box.setSuffix(' m')

        self.weight_label = QtWidgets.QLabel("Weight: ")
        self.weight_box = QtWidgets.QDoubleSpinBox()
        self.weight_box.setRange(0, 400)
        self.weight_box.setDecimals(2)
        self.weight_box.setSuffix(' kg')

        self.telegram_label = QtWidgets.QLabel("Telegram - username: ")
        self.telegram_box = QtWidgets.QLineEdit()

        self.thingspeak_label = QtWidgets.QLabel("ThingSpeak - key: ")
        self.thingspeak_box = QtWidgets.QLineEdit()

        self.doctor_label = QtWidgets.QLabel("Doctor - name surname: ")
        self.doctor_box = QtWidgets.QLineEdit()    

        self.addp_button = QtWidgets.QPushButton("Add")
        self.back_button = QtWidgets.QPushButton("Back")

        ''' Define position'''
        self.grid_layout.addWidget(self.patient_label, 1, 0)
        self.grid_layout.addWidget(self.patient_box, 1, 1, 1, 2)
        self.grid_layout.addWidget(self.age_label, 2, 0)
        self.grid_layout.addWidget(self.age_box, 2, 1, 1, 1)
        self.grid_layout.addWidget(self.height_label, 3, 0)
        self.grid_layout.addWidget(self.height_box, 3, 1, 1, 1)
        self.grid_layout.addWidget(self.weight_label, 4, 0)
        self.grid_layout.addWidget(self.weight_box, 4, 1, 1, 1)
        self.grid_layout.addWidget(self.telegram_label, 5, 0)
        self.grid_layout.addWidget(self.telegram_box, 5, 1, 1, 2)
        self.grid_layout.addWidget(self.thingspeak_label, 6, 0)
        self.grid_layout.addWidget(self.thingspeak_box, 6, 1, 1, 2)
        self.grid_layout.addWidget(self.doctor_label, 7, 0)
        self.grid_layout.addWidget(self.doctor_box, 7, 1, 1, 2)

        self.grid_layout.addWidget(self.addp_button, 8, 1)
        self.grid_layout.addWidget(self.back_button, 8, 2)

        self.addp_button.clicked.connect(self.post_patient)

    def closeEvent(self):
        reply = QtWidgets.QMessageBox.question(self, 'Error', 'Insert valid data',
        QtWidgets.QMessageBox.Ok)
        if reply == QtWidgets.QMessageBox.Ok:
            sys.exit

    def added_patient(self):
        add_patient_label = QtWidgets.QLabel("Patient %s inserted" %(self.patient_box.text()))
        for cnt in reversed(range(self.grid_layout.count()-1)):
            widget = self.grid_layout.takeAt(cnt).widget()
            if widget is not None:
                widget.deleteLater()
    
        self.grid_layout.addWidget(add_patient_label, 1, 0, 1, -1)
    
    def check_already_exists(self):
        wrong_patient_label = QtWidgets.QLabel("Patient: %s already exists" %(self.patient_box.text()))
        text_patient_label = QtWidgets.QLabel("Impossible to insert patient")
        for cnt in reversed(range(self.grid_layout.count()-1)):
            widget = self.grid_layout.takeAt(cnt).widget()
            if widget is not None:
                widget.deleteLater()
    
        self.grid_layout.addWidget(wrong_patient_label, 1, 0, 1, -1)
        self.grid_layout.addWidget(text_patient_label, 2, 0, 1, -1)

    def post_patient(self):
        self.patient_dict = WebClient().get_patients()
        if self.patient_box.text() in self.patient_dict.values():
            return self.check_already_exists()

        elif self.patient_box.text() == '' or int(self.age_box.text()) == 0 or self.telegram_box.text() == '' or self.thingspeak_box.text() == '' or self.doctor_box.text() == '' :
            return self.closeEvent()

        else:
            msg = {
                    "name"     : self.patient_box.text(),
                    "age"      : str(int(self.age_box.text())),
                    "height"   : str(float(self.height_box.text().replace(',','.').removesuffix(' m'))),
                    "weight"   : str(float(self.weight_box.text().replace(',','.').removesuffix(' kg'))),
                    "usernameT"   : self.telegram_box.text(),
                    "keyTS"    : self.thingspeak_box.text(),
                    "doctor"   : self.doctor_box.text()
                }
            
            self.added_patient()

            return WebClient().post_patient(msg)


class ManagePatient(QtWidgets.QWidget):
    """ MANAGE PATIENT window layout """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.varcontrol = 0
        self.nmod = 0
        
        ''' Define data to insert'''
        self.patient_label = QtWidgets.QLabel("Patient")
        self.patient_box = QtWidgets.QComboBox()               #dropdown menu        
        self.patient_dict = WebClient().get_patients()
        
        for k,v in self.patient_dict.items():        #add items to dropdown menu
            self.patient_box.addItem(v)

        if len(self.patient_dict.items()):
            ind = self.patient_box.currentIndex()
            self.info_patient = WebClient().get_info_patient(list(self.patient_dict.keys())[ind])
            
            #print(self.info_patient)
            self.age_label = QtWidgets.QLabel("Age: ")
            self.age_box = QtWidgets.QLineEdit(self.info_patient['age'])
            self.age_box.setReadOnly(True)

            self.height_label = QtWidgets.QLabel("Height: ")
            self.height_box = QtWidgets.QLineEdit(self.info_patient['height'])
            self.height_box.setReadOnly(True)
            

            self.weight_label = QtWidgets.QLabel("Weight: ")
            self.weight_box = QtWidgets.QLineEdit(str(self.info_patient['weight']))
            self.weight_box.setReadOnly(True)

            self.telegram_label = QtWidgets.QLabel("Telegram - username: ")
            self.telegram_box = QtWidgets.QLineEdit(self.info_patient["usernameT"])
            #self.telegram_box.setReadOnly(True)

            self.thingspeak_label = QtWidgets.QLabel("ThingSpeak - key: ")
            self.thingspeak_box = QtWidgets.QLineEdit(self.info_patient["keyTS"])
            #self.thingspeak_box.setReadOnly(True)

            self.doctor_label = QtWidgets.QLabel("Doctor - name surname: ")
            self.doctor_box = QtWidgets.QLineEdit(self.info_patient['doctor'])
            #self.doctor_box.setReadOnly(True)

            self.delp_button = QtWidgets.QPushButton('Delete')
            self.back_button = QtWidgets.QPushButton('Back')
            self.back_button.setObjectName("Back")
            self.modp_button = QtWidgets.QPushButton('Save')
            self.back_button1 = QtWidgets.QPushButton('Back')

            self.grid_layout.addWidget(self.patient_label, 1, 0)
            self.grid_layout.addWidget(self.patient_box, 1, 1, 1, 2)
            self.grid_layout.addWidget(self.age_label, 2, 0)
            self.grid_layout.addWidget(self.age_box, 2, 1, 1, 2)
            self.grid_layout.addWidget(self.height_label, 3, 0)
            self.grid_layout.addWidget(self.height_box, 3, 1, 1, 2)
            self.grid_layout.addWidget(self.weight_label, 4, 0)
            self.grid_layout.addWidget(self.weight_box, 4, 1, 1, 2)
            self.grid_layout.addWidget(self.telegram_label, 5, 0)
            self.grid_layout.addWidget(self.telegram_box, 5, 1, 1, 2)
            self.grid_layout.addWidget(self.thingspeak_label, 6, 0)
            self.grid_layout.addWidget(self.thingspeak_box, 6, 1, 1, 2)
            self.grid_layout.addWidget(self.doctor_label, 7, 0)
            self.grid_layout.addWidget(self.doctor_box, 7, 1, 1, 2)
            self.grid_layout.addWidget(self.delp_button,8,0)
            self.grid_layout.addWidget(self.back_button,8,2)

            self.delp_button.clicked.connect(self.delete_patient)
            self.patient_box.currentIndexChanged.connect(self.dropInfo)
            
            self.telegram_box.textChanged.connect(self.identifyModify)
            self.thingspeak_box.textChanged.connect(self.identifyModify)
            self.doctor_box.textChanged.connect(self.identifyModify)
        else:
            print("NoPatient")
            self.back_button = QtWidgets.QPushButton('Back')
            self.back_button.setObjectName("Back")
            self.back_button1 = QtWidgets.QPushButton('Back')
            self.grid_layout.addWidget(self.back_button,7, 1, 3, 1)

    def closeEvent(self):
        reply = QtWidgets.QMessageBox.question(self, 'Error', 'Insert valid data',
        QtWidgets.QMessageBox.Ok)
        if reply == QtWidgets.QMessageBox.Ok:
            sys.exit
    
    def identifyModify(self):
        sender_widget = self.sender()
    
        if self.varcontrol == 0:
            self.grid_layout.addWidget(self.modp_button,8,1)
            self.modp_button.clicked.connect(self.modified_patient)

        if sender_widget == self.telegram_box:
            self.tg = str(self.telegram_box.text())            
            self.varcontrol += 1
        elif sender_widget == self.thingspeak_box:
            self.ts = str(self.thingspeak_box.text())
            self.varcontrol += 1
        elif sender_widget == self.doctor_box:
            self.dc = str(self.doctor_box.text())
            self.varcontrol += 1

    
    def modified_patient(self):
        telegram = str(self.telegram_box.text())
        thingspeak = str(self.thingspeak_box.text())
        doctor = str(self.doctor_box.text())
        
        msg = {
                    'name'          : self.patient_box.currentText(),
                    'doctor'        : doctor.rstrip(),
                    'keyTS'  : thingspeak.rstrip(),
                    "usernameT" : telegram.rstrip()
                }
                
        WebClient().mod_patient(msg)
        mod_patient_label = QtWidgets.QLabel("Patient: %s modified" %(str(self.info_patient['name'])))        
        for cnt in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(cnt)
            if item.widget() is not None and item.widget().objectName() != "Back":
                self.grid_layout.removeItem(item)
                item.widget().setParent(None)
    
        self.grid_layout.addWidget(mod_patient_label, 1, 0, 1, -1)

    
    def dropInfo(self):
        self.varcontrol = 0
        self.modp_button.deleteLater()
        self.modp_button = QtWidgets.QPushButton('Save')
        ind = self.patient_box.currentIndex()
        self.info_patient = WebClient().get_info_patient(list(self.patient_dict.keys())[ind])
        #print(self.info_patient)
        self.age_box.clear()
        self.height_box.clear()
        self.weight_box.clear()

        self.doctor_box.deleteLater()
        self.telegram_box.deleteLater()
        self.thingspeak_box.deleteLater()

        self.telegram_box = QtWidgets.QLineEdit(self.info_patient["usernameT"])
        self.thingspeak_box = QtWidgets.QLineEdit(self.info_patient["keyTS"])
        self.doctor_box = QtWidgets.QLineEdit(self.info_patient['doctor'])

        self.grid_layout.addWidget(self.telegram_box, 5, 1, 1, 2)
        self.grid_layout.addWidget(self.thingspeak_box, 6, 1, 1, 2)
        self.grid_layout.addWidget(self.doctor_box, 7, 1, 1, 2)

        self.age_box.insert(self.info_patient['age'])
        self.height_box.insert(self.info_patient['height'])
        self.weight_box.insert(str(self.info_patient['weight']))

        self.telegram_box.textChanged.connect(self.identifyModify)
        self.thingspeak_box.textChanged.connect(self.identifyModify)
        self.doctor_box.textChanged.connect(self.identifyModify)
        

    def delete_patient(self):
        delete_patient_label = QtWidgets.QLabel("Patient: %s , deleted" %(self.patient_box.currentText()))
        for cnt in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(cnt)
            if item.widget() is not None and item.widget().objectName() != "Back":
                self.grid_layout.removeItem(item)
                item.widget().setParent(None)

        ind = self.patient_box.currentIndex()
        params = {'patientID' : list(self.patient_dict.keys())[ind]}
        self.grid_layout.addWidget(delete_patient_label, 1, 0, 1, -1)
        return WebClient().delete_patient(params)


class ManageDevice(QtWidgets.QWidget):
    """ MANAGE DEVICE window layout """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QtWidgets.QGridLayout(self)

        ''' Define data to insert'''
        # Add a label and a line edit to the form layout
        self.patient_label = QtWidgets.QLabel("Patient")
        self.patient_box = QtWidgets.QComboBox()               #dropdown menu
                
        self.patient_dict = WebClient().get_patients()
        for k,v in self.patient_dict.items():        #add items to dropdown menu
            self.patient_box.addItem(v)

        self.device_availe = {
                                "dev1" : "wave",
                                "dev2" : "core",
                                "dev3" : "pulse",
                                "dev4" : "gluco"
                            }

        self.dev1_box = QtWidgets.QCheckBox(list(self.device_availe.values())[0])
        self.dev2_box = QtWidgets.QCheckBox(list(self.device_availe.values())[1])
        self.dev3_box = QtWidgets.QCheckBox(list(self.device_availe.values())[2])
        self.dev4_box = QtWidgets.QCheckBox(list(self.device_availe.values())[3])

        ind = self.patient_box.currentIndex()
        #params = {'patientID' : list(self.patient_dict.keys())[ind]}
        devices_dict = WebClient().get_devices(list(self.patient_dict.keys())[ind])
        
        self.state_device = []
        for i in range(4):
            if list(self.device_availe.values())[i] in list(devices_dict.values()):
                self.state_device.append(1)
            else:
                self.state_device.append(0)

        self.status_check()

        self.save_button = QtWidgets.QPushButton("Save")
        self.back_button = QtWidgets.QPushButton("Back")

        self.grid_layout.addWidget(self.patient_label, 1, 1)
        self.grid_layout.addWidget(self.patient_box, 1, 2, 1, 2)
        self.grid_layout.addWidget(self.dev1_box)
        self.grid_layout.addWidget(self.dev2_box)
        self.grid_layout.addWidget(self.dev3_box)
        self.grid_layout.addWidget(self.dev4_box)
        self.grid_layout.addWidget(self.save_button,7, 1)
        self.grid_layout.addWidget(self.back_button,7, 3)

        self.patient_box.currentIndexChanged.connect(self.device_drop)
        self.save_button.clicked.connect(self.save_devices)
        self.open_new_panel()

    def open_new_panel(self):
        self.new_panel = QtWidgets.QGridLayout()

    def device_drop(self):
        ind = self.patient_box.currentIndex()
        #params = {'patientID' : list(self.patient_dict.keys())[ind]}
        devices_dict = WebClient().get_devices(list(self.patient_dict.keys())[ind])
        self.state_device = []
        for k in range(4):
            
            if list(self.device_availe.values())[k] in list(devices_dict.values()):
                self.state_device.append(True)
            else:
                self.state_device.append(False)
        
        return self.status_check()
    
    def status_check(self): 
        self.dev1_box.setChecked(self.state_device[0])
        self.dev2_box.setChecked(self.state_device[1])
        self.dev3_box.setChecked(self.state_device[2])
        self.dev4_box.setChecked(self.state_device[3])
    
    def status_checkbox_save(self): 
        state_save = []
        state_save.append(self.dev1_box.isChecked())
        state_save.append(self.dev2_box.isChecked())
        state_save.append(self.dev3_box.isChecked())
        state_save.append(self.dev4_box.isChecked())

        return state_save

    def changed_patient(self):
        add_patient_label = QtWidgets.QLabel("Changes saved")
        for cnt in reversed(range(self.grid_layout.count()-1)):
            widget = self.grid_layout.takeAt(cnt).widget()
            if widget is not None:
                widget.deleteLater()
    
        self.grid_layout.addWidget(add_patient_label, 1, 0, 1, -1)


    def save_devices(self):
        ind = self.patient_box.currentIndex()
        #params = {'patientID' : list(self.patient_dict.keys())[ind]}
        devices_dict = WebClient().get_devices(list(self.patient_dict.keys())[ind])
        state_save = self.status_checkbox_save()

        for k in range(len(self.device_availe.items())):
            if state_save[k] != self.state_device[k]:
                ind_dev = k
                ind_p = self.patient_box.currentIndex()
                if state_save[k] == False:
                    index = list(devices_dict.values()).index(list(self.device_availe.values())[ind_dev])
                    WebClient().delete_device(pID = list(self.patient_dict.keys())[ind_p], dID=list(devices_dict.keys())[index])

                else:
                    msg = {
                            'patientID': list(self.patient_dict.keys())[ind_p], 
                            'name': list(self.device_availe.values())[ind_dev]
                          }
                    WebClient().post_device(msg)
                    # self.add_device()       # aggiungi
        
        self.changed_patient()

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
