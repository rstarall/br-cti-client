import os
import ipaddress
import nmap
import datetime
import threading
import socket
import struct
import psutil
import pymysql
import requests
import time
import traceback
import signal
import enum
# import netifaces as ni
from configparser import ConfigParser
from pathlib import Path
from bs4 import BeautifulSoup
from multiprocessing import Lock

nmap = nmap.PortScanner()
conf_dict = {}
local_ip_list = []
scan_nic_ip: str
scan_rst = {}
scan_rst['networks'] = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/82.0.4051.0 Safari/537.36 Edg/82.0.425.0'}
lock = Lock()


class State(enum.Enum):
    Init = 0
    Running = 1
    Exit = 2


state = State.Init


class DB_Conf(object):
    def __init__(self) -> None:
        self.host = None
        self.port = None
        self.username = None
        self.password = None
        self.database = None
        self.table = None
        self.charset = None


def logMessage(logStr, level="Notice"):
    lock.acquire()
    path = "/var/log/portscan/"
    if (not Path(path).is_dir()):
        os.mkdir(path)
    logfile = "portscan-"+str(datetime.date.today())+".log"
    f = open(path+logfile, "a")
    if (level != "Exception"):
        f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) +
                " "+level+": "+logStr+"\n")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) +
              " "+level+": "+logStr+"\n")
    else:
        print(logStr)
        f.write(traceback.format_exc())
    f.close

    lock.release()


def tcp_scan(subnet, ip_list, gateway=""):  # TCP扫描

    node_list = []
    masscan_rs_list = []
    if (isinstance(ip_list, list) and len(ip_list) > 1):
        scan_ip = ' '.join([str(i) for i in ip_list])
        logMessage("tcp_scan: use ip_list="+scan_ip)
        # cmd_rst = os.popen(
        #     'masscan -p 1-65535 --exclude-port 6000 --rate 100000 --wait 3' + scan_ip)
        for ip in ip_list:
            if ip == gateway:
                node = {}
                node['ports'] = []
                node['ip'] = ip
                node_list.append(node)
                continue
            cmd = f'masscan -p 1-65535 --exclude-port 6000 --rate 100000 --wait 3 \
                    --interface br-int --router-ip {ip} {ip}'
            logMessage(f"command: {cmd}")
            cmd_rst = os.popen(cmd)
            lines = cmd_rst.read().split('\n')
            lines.pop()
            if len(lines) > 0:
                masscan_rs_list.extend(lines)
    elif (isinstance(ip_list, str)):
        scan_ip = ip_list
        logMessage("tcp_scan: use ip_list="+scan_ip)
        cmd_rst = os.popen(
            'masscan -p 1-65535 --exclude-port 6000 --rate 100000 --wait 3' + scan_ip)
        masscan_rs_list = cmd_rst.read().split('\n')
        masscan_rs_list.pop()
    else:
        logMessage("tcp_scan: use subnet="+subnet)
        # gateway = ni.gateways()['default'][ni.AF_INET][0]
        # cmd = 'masscan -p 1-65535 --exclude-port 6000 --rate 100000 --wait 3 --interface '+conf_dict['default_nic'] + " --router-ip " + gateway +" " + subnet
        gateway_mac = json.loads(subprocess.getoutput("ovs-vsctl get interface br-int mac_in_use"))
        cmd = f'masscan -p 1-65535 --exclude-port 6000 --exclude {scan_nic_ip} --rate 100000 --wait 3 \
            --interface scan_nic --router-ip {gateway} --router-mac {gateway_mac} {subnet}'
        logMessage(f"command: {cmd}")
        cmd_rst = os.popen(cmd)
        masscan_rs_list = cmd_rst.read().split('\n')
        masscan_rs_list.pop()

    # 处理tcp扫描的结果，根据ip进行合并
    if (len(masscan_rs_list) > 0):
        for discover in masscan_rs_list:
            ip = discover.split(' ')[5]
            port = discover.split(' ')[3].split('/')[0]
            bfind = False
            if (len(node_list)):
                for node in node_list:
                    if (ip == node['ip']):
                        port_info = {}
                        port_info['port'] = port
                        port_info['trans_proto'] = 'tcp'
                        node['ports'].append(port_info)
                        bfind = True
                        break
            if (bfind == False):
                node = {}
                node['ports'] = []
                node['ip'] = ip
                port_info = {}
                port_info['port'] = port
                port_info['trans_proto'] = 'tcp'
                node['ports'].append(port_info)
                node_list.append(node)
    else:
        logMessage("tcp_scan fail", level="Error")
    return node_list


def getTitle(ip, port):
    try:
        url = "http://"+ip+":"+port
        response = requests.get(url, headers=headers, verify=False, timeout=3)
        html = BeautifulSoup(response.text, 'html.parser')
        title = html.find_all("title")
        if (len(title) and response.status_code != 400):
            return title[0].string
        elif (len(title)):
            https_url = "https://"+ip+":"+port
            https_response = requests.get(
                https_url, headers=headers, verify=False, timeout=3)
            https_html = BeautifulSoup(https_response.text, 'html.parser')
            https_title = https_html.find_all("title")
            if (len(https_title)):
                return https_title[0].string
    except Exception as e:
        logMessage(e, level="Exception")
    return None


def service_scan(vlan, subnet, node, scan_nic):  # 服务识别
    logMessage(f"service scaning {node['ip']}")
    try:
        ip = node['ip']
        port_list = []
     # 单个节点提取端口 一次扫描识别
        port_count = 0
        port_argv = None
        if ('ports' in node):
            for port_index in node['ports']:
                port_list.append(port_index['port'])
                port_count += 1
            port_argv = ','.join([str(i) for i in port_list])
        else:
            node['ports'] = ''
        ret = {}
        count = 3
        while (count > 0):
            if (scan_nic != None):
                logMessage(f"nmap scan -Pn -A -e {scan_nic} {ip} {port_argv}")
                ret = nmap.scan(
                    ip, port_argv, arguments='-Pn -A -e ' + scan_nic)
            else:
                logMessage(f"nmap scan -Pn -A {ip} {port_argv}")
                ret = nmap.scan(
                    ip, port_argv, arguments='-Pn -A')
            if (len(ret['scan']) != 0):
                logMessage(f'result of {ip}: {ret}')
                break
            logMessage(f'result of {ip}: {ret}')
            count = count-1

        if (ip in ret['scan']):
            node['owned'] = 0
            if ('mac' in ret['scan'][ip]['addresses']):
                mac = ret['scan'][ip]['addresses']['mac']
                node['mac'] = mac
                if (mac in ret['scan'][ip]['vendor']):
                    mac_vendor = ret['scan'][ip]['vendor'][mac]
                    node['mac_vendor'] = mac_vendor
            if ('osmatch' in ret['scan'][ip] and len(ret['scan'][ip]['osmatch']) > 0):
                node['os_name'] = ret['scan'][ip]['osmatch'][0]['name']
                node['os_type'] = ret['scan'][ip]['osmatch'][0]['osclass'][0]['osfamily']
                node['device_type'] = ret['scan'][ip]['osmatch'][0]['osclass'][0]['type']

            if ('ports' in node):
                for port_index in node['ports']:
                    port = port_index['port']
                    proto = port_index['trans_proto']
                    port_info = ret['scan'][ip][proto][int(port)]
                    if ('name' in port_info):
                        service = port_info['name']
                        port_index['service'] = service
                        s = service.lower()
                        if ("http" in s and 'script' in port_info and "http-title" in port_info['script']):
                            title = getTitle(ip, port)
                            if (title):
                                title = title.strip('\n\t')
                                logMessage(ip + ":"+port+" title: "+title)
                                port_index['title'] = title
                    service_product = ret['scan'][ip][proto][int(
                        port)]['product']
                    if len(service_product) > 0:
                        service_version = ret['scan'][ip][proto][int(
                            port)]['version']
                        if len(service_version) > 0:
                            port_index['version'] = service_product + \
                                ' ' + service_version
                        else:
                            port_index['version'] = service_product
        PostScanRst(vlan, subnet, node)
        return True
    except Exception as e:
        logMessage(ip + " service scan Exception")
        logMessage(e, level="Exception")
        return False


def IsLocalNet(subnet):
    try:
        scan_network = ipaddress.ip_network(subnet)
        for local_ip in local_ip_list:
            if ipaddress.ip_address(local_ip) in scan_network:
                return True
    except Exception as e:
        logMessage(e, level="Exception")

    return False


def is_IP_Virtual(ip, vmlist):
    if (ip in vmlist):
        return True
    return False


def getVmList():
    vmlist = []
    con = ConnectDB("VMDB")
    if (con == None):
        return None
    cur = con.cursor()
    sql = 'SELECT ip FROM '+conf_dict["VMDB"].table
    cur.execute(sql)
    vip_list = cur.fetchall()
    vmlist.clear()
    for ip in vip_list:
        vmlist.append(ip[0])
    cur.close()
    con.close()
    return vmlist


def IP_Scan(subnet, ip_list):  # 本网段IP扫描，寻找空闲的IP地址，配置这个IP地址用于后续扫描

    # if (True == IsLocalNet(subnet)):
    #     return conf_dict['default_nic']

    # 获取掩码和网段
    NetMask = int(subnet.split('/')[1])
    Net = socket.ntohl(struct.unpack(
        "I", socket.inet_aton(subnet.split('/')[0]))[0])
    # 根据掩码获取机器地址范围
    IP_Range = 2 ** (32 - NetMask) - 1
    # 根据掩码获取真实网段
    Real_Net = Net & ~(2 ** (32 - NetMask) - 1)
    # 提前选择ip 1.1.1.1 防止交因为arp报文源地址不符合当前网段被交换机过滤
    # Select_IP = socket.inet_ntoa(struct.pack('I', socket.htonl(Real_Net + 1)))
    # arp 扫描
    cmd_rst = os.popen('arp-scan -g -r 3 --arpspa 1.1.1.1 --interface=scan_nic ' +
                       subnet+'|egrep "([0-9a-f][0-9a-f]:){5}"|sed -n "2,255p"')
    arp_rst = cmd_rst.read()
    arp_list = arp_rst.split('\n')

    # arp扫描有结果
    if (len(arp_list) > 1):
        vmlist = getVmList()
        for index in arp_list:
            ip = index.split('\t')[0]
            # 获取指定网段ip列表
            if (ip != '' and False == is_IP_Virtual(ip, vmlist)):
                ip_list.append(ip)
        arp_list.clear()
        if (len(ip_list) == 0):
            return None
        # 从ip中遍历寻找临时不冲突的ip
        for i in range(1, IP_Range - 1):
            ip_int = Real_Net+i
            ip_str = socket.inet_ntoa(struct.pack('I', socket.htonl(ip_int)))
            if ip_str not in ip_list:
                # os.system("route add -net " + subnet + " metric 200 scan_nic")
                os.system('ifconfig scan_nic ' +
                          ip_str+'/'+str(NetMask)+' up')
                global scan_nic_ip
                scan_nic_ip = ip_str
                return "scan_nic"

    # 扫描网段跨路由器
    else:
        return conf_dict["default_nic"]

"""
这段代码的功能是为VLAN创建一个虚拟网络接口，并配置其基本属性：
定义了一个名为Init_VirtualDevice的函数，用于初始化虚拟网络设备。
vlan参数传入的值没有在函数体中体现
"""
def Init_VirtualDevice(vlan):  # 新建虚拟设备

    device = conf_dict['scan_nic']
    os.system("ovs-vsctl add-port br-int scan_nic -- set interface scan_nic type=internal ")
    """
    使用Open vSwitch的命令行工具ovs-vsctl添加虚拟设备：
    -   add-port br-int scan_nic：将名为scan_nic的接口添加到br-int网桥
    - --set interface scan_nic type=internal：将接口类型设置为internal，表示虚拟设备由系统内核管理。
    """
    os.system("ip link set dev scan_nic address fe:10:fe:10:fe:10")
    """
    使用ip命令设置虚拟设备的MAC地址为....。
    此MAC地址是硬编码的，需要确保它在网络中是唯一的，以避免冲突。
    """
    os.system("ip link set scan_nic up") # 将虚拟设备设置为启用状态(up)，使其可以正常工作
    logMessage("create virtual nic : scan_nic")


def Delete_VirtualDevice():  # 删除虚拟设备

    logMessage("delete virtual nic : scan_nic")
    os.system('ovs-vsctl del-port scan_nic')
    # os.system('ip link delete scan_nic')


def PortScan():  # 端口扫描

    start_scan_time = datetime.datetime.now()
    for network in scan_rst['networks']:
        vlan = network['vlan']
        Thread_List = []
        for subnet_dict in network['subnets']:
            subnet = subnet_dict['subnet']
            gateway = subnet_dict['gateway']
            # 配置虚拟设备
            # if (vlan != '0'):
            # if (vlan != '0' and False == IsLocalNet(subnet)):
            if (vlan != '0'):
                Init_VirtualDevice(vlan)
            # 获取subnet下的ip列表
            ip_list = []
            start_time = datetime.datetime.now()
            logMessage("ARP Scaning: "+subnet+"······")
            scan_nic = IP_Scan(subnet, ip_list)
            if (scan_nic == None and len(ip_list) == 0):
                logMessage("No real host in this subnet: "+subnet)
                Delete_VirtualDevice()
                continue
            Delete_VirtualDevice()
            logMessage("TCP Scaning: "+subnet+"······")
            # TCP端口扫描
            node_list = tcp_scan(subnet, ip_list, gateway)
            logMessage("tcp_scan complete!")

            # add IPs that have no open ports
            for ip in ip_list:
                if not any(filter(lambda n: n['ip'] == ip, node_list)):
                    node_list.append({'ip': ip, 'ports': []})

            if (len(node_list) < 1):
                logMessage("TCP Scaning "+subnet+" Fail", level="Error")
                logMessage("Scan Next Subnet", level="Error")
                continue
            logMessage("Service Identifying: "+subnet+"······")
            vmlist = getVmList()
            for node in node_list:
                try:
                    ip = node['ip']
                    if (ip != '' and True == is_IP_Virtual(ip, vmlist)):
                        continue
                    # service_scan(vlan, subnet, node, scan_nic)
                    # TCP端口服务识别
                    thread = threading.Thread(
                        target=service_scan, args=(vlan, subnet, node, "br-int"))
                    Thread_List.append(thread)
                    thread.start()
                except:
                    pass
            for thread in Thread_List:
                thread.join()
            Thread_List.clear()
            subnet_dict['nodes'] = node_list
            end_time = datetime.datetime.now()
            logMessage("scaning " + subnet + " complete")
            logMessage(subnet+" Scan cost " +
                       str((end_time - start_time).seconds) + " s")
            # Delete_VirtualDevice()
    # 数据库结果更新
    UpdateDB()
    # 网段拓扑判断
    NetTopology()
    end_time = datetime.datetime.now()
    logMessage("Total Time Cost: " +
               str((end_time - start_scan_time).seconds)+" s")


def GetSubnetARG():  # 从数据库获取扫描网段

    logMessage("get net conf from DataBase")
    con = ConnectDB("SubnetParamDB")
    if (con == None):
        return False
    cur = con.cursor()
    sql = 'SELECT vlan,subnet,gateway FROM ' + \
        conf_dict["SubnetParamDB"].table
    cur.execute(sql)
    net_config = cur.fetchall()
    if (len(net_config) == 0):
        logMessage("No subnet needs to be scanned", level="Error")
        return False
    scan_rst.clear()
    scan_rst['networks'] = []
    for config in net_config:
        vlan = config[0]
        subnet = config[1]
        gateway = config[2]
        """
        执行系统命令ping来检测网关的连通性：
        -  w 1：设置超时时间为1秒。
        -  c 1：发送1一个ICMP数据包
        -  > /dev/null: 将ping的输出重定向到/dev/null,以便不在控制台显示。
        os.system()返回命令的退出状态码：
        - 0表示成功，目标可达
        - 非0表示失败，目标不可达
        """
        if (0 != os.system("ping -w 1 -c 1 " + gateway + "> /dev/null")):
            sql = "UPDATE " + \
                conf_dict["SubnetParamDB"].table + \
                " SET status=1 where vlan="+vlan
            con.commit()
            continue
        else:
            sql = "UPDATE " + \
                conf_dict["SubnetParamDB"].table + \
                " SET status=0 where vlan="+vlan
            con.commit()
        network = {}
        network['vlan'] = vlan
        network['subnets'] = []
        subnet_dict = {}
        subnet_dict['subnet'] = subnet
        subnet_dict['gateway'] = gateway
        # NetMask = int(subnet.split('/')[1])
        # Net = socket.ntohl(struct.unpack(
        #     "I", socket.inet_aton(subnet.split('/')[0]))[0])
        # # 根据掩码获取机器地址范围
        # IP_Range = 2 ** (32 - NetMask) - 1
        # # 根据掩码获取真实网段
        # Real_Net = Net & ~(2 ** (32 - NetMask) - 1)
        # IPMIN = Real_Net + 1
        # IPMAX = Real_Net + IP_Range - 1
        # subnet_dict['IPMIN'] = IPMIN
        # subnet_dict['IPMAX'] = IPMAX
        network['subnets'].append(subnet_dict)
        scan_rst['networks'].append(network)
    cur.close()
    con.close()


    con = ConnectDB("PortScanRstDB")
    if (con == None):
        return False

    con = ConnectDB("VMDB")
    if (con == None):
        return False

    return True


def PostScanRst(vlan, subnet, node):  # 上传扫描结果

    try:
        con = ConnectDB("PortScanRstDB")
        if (con == None):
            return False
        cur = con.cursor()
        # IP地址
        ip = '"' + node['ip'] + '"'
        # MAC地址
        if 'mac' in node:
            mac = '"' + node['mac'] + '"'
        else:
            mac = 'NULL'
        # 设备厂商
        if 'mac_vendor' in node:
            mac_vendor = '"' + node['mac_vendor'] + '"'
        else:
            mac_vendor = 'NULL'
        # 设备类型
        if 'device_type' in node:
            device_type = '"' + node['device_type'] + '"'
        else:
            device_type = 'NULL'
        # 操作系统名称
        if 'os_name' in node:
            os_name = '"' + node['os_name'] + '"'
        else:
            os_name = 'NULL'

        # Microsoft Windows 7 SP0 - SP1, Windows Server 2008 SP1, Windows Server 2008 R2, Windows 8, or Windows 8.1 Update 1
        # Microsoft Windows 10 1709 - 1909
        if 'Windows 7' in os_name:
            os_name='Windows 7'

        # 操作系统类型
        if 'os_type' in node:
            os_type = '"' + node['os_type'] + '"'
        else:
            os_type = 'NULL'
        # 端口
        if 'ports' in node:
            ports = str(node['ports']).replace("'", '\"')
        else:
            ports = ''
        modify_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 构建sql语句
        cur.execute('SELECT count(id) FROM ' +
                    conf_dict["PortScanRstDB"].table+' where ip ='+ip)
        count = cur.fetchone()[0]
        if (count > 0):
            if ('mac' not in node):
                argv = " set vlan={vlan}, subnet='{subnet}', status=0, owned={owned}, ports='{ports}',modify_time='{modify_time}'".format(
                    vlan=vlan, subnet=subnet, ip=ip, owned=0, ports=ports, modify_time=modify_time)
            else:
                argv = " set vlan={vlan}, subnet='{subnet}', status=0, mac={mac}, mac_vendor={mac_vendor}, device_type={device_type}, owned={owned}, os_name={os_name}, os_type={os_type}, ports='{ports}',modify_time='{modify_time}'".format(
                    vlan=vlan, subnet=subnet, ip=ip, mac=mac, mac_vendor=mac_vendor, device_type=device_type,
                    owned=0, os_name=os_name, os_type=os_type, ports=ports, modify_time=modify_time)

            sql = ' UPDATE ' + \
                conf_dict["PortScanRstDB"].table + argv+' where owned=0 and ip =' + ip
        else:
            argv = "({level}, {status}, {vlan}, '{subnet}', {ip}, {mac}, {mac_vendor}, {device_type}, {owned}, {os_name}, {os_type}, '{ports}' ,'{modify_time}')".format(
                level=0, status=0, vlan=vlan, subnet=subnet, ip=ip, mac=mac, mac_vendor=mac_vendor, device_type=device_type,
                owned=0, os_name=os_name, os_type=os_type, ports=ports, modify_time=modify_time)
            sql = 'INSERT INTO ' + conf_dict["PortScanRstDB"].table + \
                ' (level, status, vlan, subnet, ip, mac, mac_vendor, device_type, owned, os_name, os_type, ports, modify_time) VALUES ' + argv
        # 执行sql语句
        affected_rows = cur.execute(sql)
        if affected_rows != 0:
            # 提交
            con.commit()
        cur.close()
        con.close()
    except Exception as e:
        logMessage(ip + " post rst Exception")
        logMessage(e, level="Exception")

"""
这段代码定义了一个简单的函数check_interface_exists，用于检查某个网络接口是否存在
- 函数作用：检查指定的网络接口名称(interface_name)是否在系统的网络接口列表中。
- 实现细节：psutil.net_if_addrs(): 返回系统中所有网络接口的地址信息。
        返回值是一个字典，键是网络接口的名称，值是该接口的地址信息(如IP地址、MAC地址等。)
        
"""
def check_interface_exists(interface_name):

    interfaces = psutil.net_if_addrs()
    if interface_name in interfaces:
        return True
    return False


def GetLocalCFG(conf_dict):  # 获取本地配置

    config_file = "/etc/portscan/PortScan.cfg"
    # config_file = "/root/portscaninterface/PortScan.cfg"
    if (not os.path.exists(config_file)):
        logMessage(config_file + " do not exist", level="Error")
        return False
    logMessage("read config:" + config_file)
    conf = ConfigParser()
    conf.read(config_file)

    confname = ["SubnetParamDB", "PortScanRstDB", "VMDB"]
    for cfname in confname:
        if not conf.has_section(cfname):
            logMessage(config_file + " does not have " +
                       cfname+" section", level="Error")
            conf.clear()
            return False
        db = DB_Conf()

        if not conf.has_option(cfname, 'host'):
            logMessage(config_file + ": section " +
                       cfname+" do not have host option", level="Error")
            conf.clear()
            return False
        db.host = conf.get(cfname, "host")

        if not conf.has_option(cfname, 'port'):
            logMessage(config_file + ": section " +
                       cfname+" do not have port option", level="Error")
            conf.clear()
            return False
        db.port = conf.get(cfname, "port")

        if not conf.has_option(cfname, 'username'):
            logMessage(config_file + ": section " +
                       cfname+" do not have username option", level="Error")
            conf.clear()
            return False
        db.username = conf.get(cfname, "username")

        if not conf.has_option(cfname, 'password'):
            logMessage(config_file + ": section " +
                       cfname+" do not have password option", level="Error")
            conf.clear()
            return False
        db.password = conf.get(cfname, "password")

        if not conf.has_option(cfname, 'database'):
            logMessage(config_file + ": section " +
                       cfname+" do not have database option", level="Error")
            conf.clear()
            return False
        db.database = conf.get(cfname, "database")

        if not conf.has_option(cfname, 'table'):
            logMessage(config_file + ": section " +
                       cfname+" do not have table option", level="Error")
            conf.clear()
            return False
        db.table = conf.get(cfname, "table")

        if not conf.has_option(cfname, 'charset'):
            logMessage(config_file + ": section " +
                       cfname+" do not have charset option", level="Error")
            conf.clear()
            return False
        db.charset = conf.get(cfname, "charset")
        conf_dict[cfname] = db
        db = None

    # 本地配置
    if not conf.has_section("local"):
        logMessage(config_file + " does not have local section", level="Error")
        conf.clear()
        return False

    if not conf.has_option("local", 'scan_nic'):
        logMessage(
            config_file + ": section do not have scan_nic option", level="Error")
        conf.clear()
        return False

    conf_dict["scan_nic"] = conf.get("local", "scan_nic")
    if (False == check_interface_exists(conf_dict["scan_nic"])):
        logMessage(
            config_file + ": scan_nic: "+conf_dict["scan_nic"]+"do not exits", level="Error")
        conf.clear()
        return False

    if not conf.has_option("local", 'default_nic'):
        logMessage(
            config_file + ": section do not have default_nic option", level="Error")
        conf.clear()
        return False

    conf_dict["default_nic"] = conf.get("local", "default_nic")
    if (False == check_interface_exists(conf_dict["default_nic"])):
        logMessage(
            config_file + ": default_nic: "+conf_dict["default_nic"]+"do not exits", level="Error")
        conf.clear()
        return False

    Delete_VirtualDevice()
    net_if_addrs = psutil.net_if_addrs()
    """
    1、获取网络接口的地址信息：
    net_if_addrs = psutil.net_if_addrs()
    -   使用psutil.net_if_addrs()获取系统中所有网络接口及其地址信息。
    -   返回值是一个字典，格式为：
        {
         "interface_name":[address_info1,address_info2,...]
        }
        "interface_name"是网络接口名称(如，eth0,lo)
        "address_info"是包含地址信息的对象，包括地址类型(IPv4,IPv6等)、实际地址、广播地址等。
    """
    for interface_name, interface_addresses in net_if_addrs.items():
        # if (interface_name == conf_dict["default_nic"]):
        for address in interface_addresses:
            # 满足条件的IPv4地址会被添加到local_ip_list列表中，并打印到控制台。
            if (address.family == socket.AF_INET and len(address.address) > 0):
                local_ip_list.append(address.address)
                print("IP Address:", address.address)
    conf.clear()
    return True


def ConnectDB(dbname):
    try:
        conn = pymysql.connect(host=conf_dict[dbname].host, password=conf_dict[dbname].password,
                           port=int(conf_dict[dbname].port), user=conf_dict[dbname].username,
                           charset=conf_dict[dbname].charset, database=conf_dict[dbname].database)
        logMessage("Connect to "+dbname+" success")
        return conn
    except:
        logMessage("Connect to "+dbname+" failed", level="Error")
        return None


def node_scan(vlan, subnet, ip):
    node_list = tcp_scan(subnet=subnet, ip_list=ip)
    if len(node_list) == 0:
        return False
    node = node_list[0]
    if (node == None):
        return False
    return service_scan(vlan, subnet, node, scan_nic=None)


def NetTopology():  # 分析网络拓扑
    logMessage("Analyzing the network topology ······")
    try:
        nodes_con = ConnectDB("PortScanRstDB")
        conf_con = ConnectDB("SubnetParamDB")
        if (nodes_con == None or conf_con == None):
            logMessage("Analyzing Failed", level="Error")
            return False
        nodes_cur = nodes_con.cursor()
        conf_cur = conf_con.cursor()

        # 清空拓扑信息
        sql = 'UPDATE ' + \
            conf_dict["PortScanRstDB"].table+" set parent_id=NULL where owned=0"
        nodes_cur.execute(sql)

        # 同vlan内寻找根节点（路由器/交换机）
        sql = 'SELECT DISTINCT vlan,subnet FROM ' + \
            conf_dict["PortScanRstDB"].table+" where vlan!=0"
        nodes_cur.execute(sql)
        vlansubnet_tuple = nodes_cur.fetchall()
        for tuple_element in vlansubnet_tuple:
            vlan = tuple_element[0]
            subnet = tuple_element[1]
            sql = 'SELECT id,device_type,ip FROM ' + \
                conf_dict["PortScanRstDB"].table+' where owned=0 and vlan='+str(vlan)
            nodes_cur.execute(sql)
            vlan_dev_list = nodes_cur.fetchall()
            sql = 'SELECT gateway FROM ' + \
                conf_dict["SubnetParamDB"].table+' where vlan='+str(vlan)
            conf_cur.execute(sql)
            Specified_gateway_ip = conf_cur.fetchone()[0]
            gateway_id = None
            for device_info in vlan_dev_list:
                device_type = device_info[1]
                ip = device_info[2]
                if (Specified_gateway_ip != None and Specified_gateway_ip == ip):
                    gateway_id = device_info[0]
                    break
                if (Specified_gateway_ip == None and (
                        (device_type != None and (device_type == "switch" or device_type == "WAP" or "router" in device_type)))
                    ):
                    gateway_id = device_info[0]
            if (gateway_id != None):
                sql = ' UPDATE ' + conf_dict["PortScanRstDB"].table + \
                    " set parent_id=" + \
                    str(gateway_id)+' where owned=0 and vlan=' + \
                    str(vlan) + ' and id!='+str(gateway_id)
                nodes_cur.execute(sql)
                nodes_con.commit()
            elif (Specified_gateway_ip != None and gateway_id == None):
                node_scan(vlan, subnet, Specified_gateway_ip)
                sql = ' UPDATE ' + conf_dict["PortScanRstDB"].table + \
                    " set parent_id=" + \
                    "(SELECT id FROM "+conf_dict["PortScanRstDB"].table+" where ip=\""+Specified_gateway_ip+"\")"+" where owned=0 and vlan=" + \
                    str(vlan) + " and ip!=\""+Specified_gateway_ip+"\""
                nodes_cur.execute(sql)
                nodes_con.commit()

        # 同网段寻找根节点
        sql = 'SELECT DISTINCT subnet FROM ' + \
            conf_dict["PortScanRstDB"].table+" where vlan=0"
        nodes_cur.execute(sql)
        subnet_tuple = nodes_cur.fetchall()
        for subnet_tuple_element in subnet_tuple:
            subnet = subnet_tuple_element[0]
            sql = 'SELECT id,device_type,ip FROM ' + \
                conf_dict["PortScanRstDB"].table+' where owned=0 and subnet=\''+subnet+'\''
            nodes_cur.execute(sql)
            subnet_dev_list = nodes_cur.fetchall()
            sql = 'SELECT gateway FROM ' + \
                conf_dict["SubnetParamDB"].table+' where subnet=\''+subnet+'\''
            conf_cur.execute(sql)
            Specified_gateway_ip = conf_cur.fetchone()[0]
            gateway_id = None
            for device_info in subnet_dev_list:
                device_type = device_info[1]
                ip = device_info[2]
                if (Specified_gateway_ip != None and Specified_gateway_ip == ip):
                    gateway_id = device_info[0]
                    break
                if (Specified_gateway_ip == None and (
                        (device_type != None and (device_type == "switch" or device_type == "WAP" or "router" in device_type)))
                    ):
                    gateway_id = device_info[0]
            if (gateway_id != None):
                sql = ' UPDATE ' + conf_dict["PortScanRstDB"].table + \
                    " set parent_id=" + \
                    str(gateway_id)+' where owned=0 and subnet=\'' + \
                    subnet+'\' and id !='+str(gateway_id)
                nodes_cur.execute(sql)
            elif (Specified_gateway_ip != None and gateway_id == None):
                node_scan(vlan, subnet, Specified_gateway_ip)
                sql = ' UPDATE ' + conf_dict["PortScanRstDB"].table + \
                    " set parent_id=" + \
                    "(SELECT id FROM "+conf_dict["PortScanRstDB"].table+" where ip=\""+Specified_gateway_ip+"\")"+" where owned=0 and subnet=\'" + \
                    subnet + "\' and ip!=\""+Specified_gateway_ip+"\""
                nodes_cur.execute(sql)
                nodes_con.commit()


        # traceroute查找
        sql = 'SELECT ip,vlan FROM ' + \
            conf_dict["PortScanRstDB"].table + \
            ' where id in (SELECT DISTINCT parent_id FROM ' + \
            conf_dict["PortScanRstDB"].table + ')'
        nodes_cur.execute(sql)
        ip_tuple = nodes_cur.fetchall()
        for ip_tuple_element in ip_tuple:
            ip = ip_tuple_element[0]
            vlan = ip_tuple_element[1]
            cmd_rst = os.popen(
                'traceroute ' + ip + ' -i' + conf_dict["default_nic"] + " -w 1 -m 10|grep -v traceroute|grep -o '(.*)'|cut -d '(' -f2|cut -d ')' -f1")
            trIpRst = cmd_rst.read().split('\n')
            level = 0
            for parent_ip in reversed(trIpRst):
                if (parent_ip == '' or parent_ip == "*" or parent_ip == ip):
                    continue
                level += 1
                sql = "SELECT id,vlan FROM " + \
                    conf_dict["PortScanRstDB"].table + \
                    ' where ip =\''+parent_ip + '\''
                nodes_cur.execute(sql)
                id_tuple = nodes_cur.fetchall()
                if (len(id_tuple) == 0):
                    continue
                parent_id = id_tuple[0][0]
                parent_vlan = id_tuple[0][1]
                sql = ' UPDATE '+conf_dict["PortScanRstDB"].table + \
                    ' set parent_id='+str(parent_id)+' where ip=\''+ip+'\''
                nodes_cur.execute(sql)
                sql = ' UPDATE '+conf_dict["PortScanRstDB"].table + \
                    ' set parent_vlan=' + \
                    str(parent_vlan)+',level =' + \
                    str(level) + ' where owned=0 and vlan='+str(vlan)
                nodes_cur.execute(sql)

        nodes_con.commit()
        nodes_cur.close()
        nodes_con.close()
        conf_cur.close()
        conf_con.close()
    except Exception as e:
        logMessage("NetTopology Fail", level="Error")
        logMessage(e, level="Exception")


def UpdateDB():  # 更新删除无效ip
    try:
        logMessage("Updating DataBase ······")
        con = ConnectDB("PortScanRstDB")
        if (con == None):
            return False
        cur = con.cursor()
        # 删除无效网段与ip
        sql = 'SELECT DISTINCT subnet FROM '+conf_dict["PortScanRstDB"].table
        cur.execute(sql)
        subnet_tuple = cur.fetchall()
        for subnet_tuple_element in subnet_tuple:
            db_subnet = subnet_tuple_element[0]
            bfind = False
            for network in scan_rst['networks']:
                subnets = network['subnets']
                for subnet in subnets:
                    if (subnet['subnet'] == db_subnet):
                        bfind = True
                        break
                if (bfind):
                    break
            if (bfind == False):
                sql = ' UPDATE ' + \
                    conf_dict["PortScanRstDB"].table + ' set status=1 ' + \
                    ' where subnet = "'+db_subnet+'" and owned=0'
                cur.execute(sql)
            else:
                sql = 'SELECT ip,mac,owned FROM ' + \
                    conf_dict["PortScanRstDB"].table + \
                    ' where subnet="' + db_subnet+'"'
                cur.execute(sql)
                node_tuple = cur.fetchall()
                for ip, mac, owned in node_tuple:
                    bfind = False
                    for node in subnet['nodes']:
                        if (ip == node['ip']):
                            bfind = True
                            break
                    if (owned == 0 and bfind == False and 0 != os.system("ping -w 1 -c 1 " + ip + " > /dev/null")):
                        sql = 'UPDATE '+conf_dict["PortScanRstDB"].table + ' set status=1 ' + \
                            ' where ip = "'+ip+'"'
                        logMessage(ip + " status=1")
                        cur.execute(sql)
        con.commit()
        cur.close()
        con.close()
    except Exception as e:
        print(e)
        logMessage(e, level="Exception")


def Notice():
    try:
        url = "http://admin:8080/api/assets/notify"
        data = "PortScan Complete!"
        res = requests.post(url=url, data=data)
        print(res.text)
    except Exception as e:
        logMessage(e, level="Exception")


def handle_sigint(signum, frame):
    logMessage('Received SIGINT')
    logMessage('Exiting······')
    global state
    state = State.Exit


def check_port_occupied(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            return True
        except OSError:
            return False


def listen():
    if (check_port_occupied("admin", 2001) == False):
        sock = socket.socket()
        sock.bind(('admin', 2001))
        sock.listen()
        global state
        while True:
            if (state == State.Exit):
                break
            conn, addr = sock.accept()
            data = conn.recv(1024)
            print(data.decode(encoding='utf-8', errors='ignore'))
            conn.send(b'HTTP/1.1 200 OK\n\nService Scan Interface\n')
            conn.close()
        sock.close()
    else:
        logMessage("port 2001 is used", level="Warning")


def PortScanInterFace():
    if os.geteuid() != 0:
        logMessage("This program must be run as root. Aborting.", level="Error")
        logMessage("Program Abort", level="Error")
        os._exit(1)
    sleep_time = 10
    Execution_interval = 5*60
    execute_time = datetime.datetime.now()
    has_executed = False
    global state
    th = threading.Thread(target=listen)
    th.start()
    state = State.Running
    while True:
        if (state == State.Exit):
            break
        interval_time = (datetime.datetime.now() - execute_time).seconds
        if (not has_executed or interval_time > Execution_interval):
            if (not GetLocalCFG(conf_dict) or not GetSubnetARG()):
                time.sleep(sleep_time)
                continue
            execute_time = datetime.datetime.now()
            logMessage("[+]PortScan Starting......\n\n")
            # 端口扫描
            PortScan()
            # http post 通知
            Notice()
            logMessage("[+]PortScan Complete!\n\n")
            has_executed = True
            future_time = (
                execute_time+datetime.timedelta(seconds=Execution_interval)).strftime('%Y-%m-%d %H:%M:%S')
            logMessage("Next Scan Time: "+future_time)
        time.sleep(sleep_time)
    th.join()


if __name__ == '__main__':
    PortScanInterFace()
