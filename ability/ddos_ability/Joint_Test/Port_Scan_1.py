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
from configparser import ConfigParser
from pathlib import Path
from bs4 import BeautifulSoup
from multiprocessing import Lock

namp = nmap.PortScanner()
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
    def __init__(self)->None:
        self.host = None
        self.port = None
        self.username = None
        self.password = None
        self.database = None
        self.table = None
        self.charset = None

def logMessage(logStr,level = "Notice"):
    lock.acquire()
    path = '/var/log/portscan/'
    if (not Path(path).is_dir()):
        os.mkdir(path)

    logfile = "portscan-"+str(datetime.date.today())+".log"
    f = open(path+logfile,"a")
    if (level !="Exception"):
        f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())+" "+level+":"+logStr+"\n")
        print()
    else:
        print(logStr)
        f.write(traceback.format_exc())
    f.close()

    lock.release()

import json
import subprocess
def tcp_scan(subnet,ip_list,gateway=""):
    node_list = []
    masscan_rs_list = []
    if (isinstance(ip_list,list) and len(ip_list)>1):
        scan_ip = ''.join([str(i) for i in ip_list])
        logMessage("tcp_scan: use ip_list="+scan_ip)

        for ip in ip_list:
            if ip==gateway:
                node = {}
                node["ports"] = []
                node['ip'] = ip
                node_list.append(node)
                continue

            cmd = f"masscan -p 1-65535 --exlude-port 6000 --rate 100000 --wait 3 --interfance br-int --rounter-ip {ip}{ip}"
            logMessage(f"command:{cmd}")
            cmd_rst = os.popen(cmd)
            lines = cmd_rst.read().split('\n')
            lines.pop()
            if len(lines)>0:
                masscan_rs_list.extend(lines)
    elif (isinstance(ip_list, str)):
        scan_ip = ip_list
        logMessage("tcp_scan: use ip_list=" + scan_ip)
        cmd_rst = os.popen(
            'masscan -p 1-65535 --exclude-port 6000 --rate 100000 --wait 3' + scan_ip)
        masscan_rs_list = cmd_rst.read().split('\n')
        masscan_rs_list.pop()
    else:
        logMessage("tcp_scan: use subnet=" + subnet)
        # gateway = ni.gateways()['default'][ni.AF_INET][0]
        # cmd = 'masscan -p 1-65535 --exclude-port 6000 --rate 100000 --wait 3 --interface '+conf_dict['default_nic'] + " --router-ip " + gateway +" " + subnet
        # 获取网络MAC地址：通过subprocess.getoutput获取网关地址接口br-int的MAC地址。
        # 这里假设你使用的是 Open vSwitch (ovs-vsctl)。
            # ovs-vsctl get interface br-int mac_in_use 返回 MAC 地址的 JSON 格式字符串。
            # 使用 json.loads 将结果解析为 Python 数据类型。
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


def getTitle(ip,port):
    pass

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

def service_scan(vlan,subnet,node,scan_nic):
    logMessage(f"service scaning {node['ip']}")
    try:
        ip = node['ip']
        port_list = []
        port_count = 0
        port_argv = None
        if ("ports" in node):
            for port_index in node['ports']:
                port_list.append(port_index['port'])
                port_count +=1
            port_argv = ','.join([str(i) for i in port_list])
        else:
            node['ports'] = ''

        ret = {}
        count = 3
        while (count>0):
            if (scan_nic !=None):
                logMessage(f'nmap scan -Pn -A -e {scan_nic} {ip} {port_argv}')
                ret = nmap.scan(ip,port_argv,arguments='-Pn, -A, -e '+scan_nic)
            else:
                logMessage(f"nmap scan -Pn -A {ip} {port_argv}")
                ret = nmap.scan(
                    ip, port_argv, arguments='-Pn -A')

                if (len(ret['scan']) != 0):
                    logMessage(f'result of {ip}: {ret}')
                    break
                logMessage(f'result of {ip}: {ret}')
                count = count - 1

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
                            if ('http' in s and 'script' in port_info and 'http-title' in port_info['script']):
                                title = getTitle(ip,port)
                                if (title):
                                    title = title.strip('\n\t')
                                    logMessage(ip+':'+port+" title: "+title)
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

            # P
            return True
    except Exception as e:
        logMessage(ip+" sevice scan Exception")
        logMessage(e,level='Exception')
        return False

def ConnectDB(dbname):
    try:
        conn = pymysql.connect(host = conf_dict[dbname].host,password=conf_dict[dbname].password,
                              port=int(conf_dict[dbname].port),user=conf_dict[dbname].username,
                               charset=conf_dict[dbname].charset, database=conf_dict[dbname].database)
        logMessage("Connect to " + dbname + " success")
        return conn
    except:
        logMessage("Connect to " + dbname + " failed", level="Error")
        return None

def node_scan(vlan,subnet,ip):
    node_list = tcp_scan(subnet=subnet,ip_list=ip)
    if len(node_list) ==0:
        return False
    node = node_list[0]
    if (node==None):
        return False
    return service_scan(vlan,subnet,node,scan_nic=None)

def NetTopology():
    pass

def GetLocalCFG():
    pass

def IP_Scan(subnet,ip_list):
    NetMask = int(subnet.split('/')[1])
    Net = socket.ntohl(struct.unpack('I',socket.inet_aton(subnet.split('/')[0]))[0])
    # 根据掩码获取机器地址范围
    IP_Range = 2 ** (32 -NetMask) - 1
    # 根据掩码获取真实网段 # ~(2**(32-NetMask)-1)按位取反，得到网络位全为1的掩码
    Real_Net = Net & ~(2**(32-NetMask)-1)

    cmd_rst = os.popen('arp-scan -g -r 3 --arpspa 1.1.1.1 --interface=scan_nic '+
                       subnet+'|egrep "([0-9a-f][0-9a-f]:){5}"|sed -n "2,255p')
    arp_rst = cmd_rst.read()
    arp_list = arp_rst.split('\n')

    if (len(arp_list)>1):
        pass


def PortScan():
    pass

def PortScanInterFace():
    pass
























