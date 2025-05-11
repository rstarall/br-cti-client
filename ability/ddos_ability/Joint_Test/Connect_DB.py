import mysql.connector

def connect_db():
  # 连接到 MariaDB  dns: "root:XTqo4mIHcy@tcp(10.2.88.19:3306)/snhoneypot?charset=utf8mb4,utf8&parseTime=True&loc=Local"
  mydb = mysql.connector.connect(
    host="10.2.88.19",
    user="root",
    password="XTqo4mIHcy",
    database="snhoneypot"
  )
  # 创建一个游标对象
  mycursor = mydb.cursor()
  return mydb,mycursor


def ip_period_select():
  mydb,mycursor = connect_db()
  '''1.1、查询IP跳变周期'''
  mycursor.execute("SELECT * FROM app_settings WHERE name = 'ip_change_period'")
  # 获取所有查询结果
  ip_result = mycursor.fetchall()
  ip_data_json = {
    "defense_id": "active_defense_subsystem",
    "name": "地面网络系统主动防御策略",
    "sid_rev": "active_defense_subsystem ",
    "execute_unit": ["IP_mutation"],#IP跳变周期
    "defend_parameter":{
      "second": 20, },
    "other":{
      "Time": "2024-5-18 15:12:18" #IP跳变发生时间
      }
  }
  ip_data_json["defend_parameter"] ["second"] = ip_result[0][4]
  ip_data_json["other"]["Time"] = ip_result[0][2].strftime("%Y-%m-%d %H:%M:%S")
  # print(ip_data_json)
  # 关闭连接
  mycursor.close()
  mydb.close()

  return ip_data_json


def ip_period_modify(ip_period):
  print(ip_period)
  mydb,mycursor = connect_db()
  '''1.2、修改IP跳变周期'''
  # mycursor.execute("UPDATE app_settings SET value =%s WHERE name = 'ip_change_period';")
  query = "UPDATE app_settings SET value = %s WHERE name = 'ip_change_period';"
  mycursor.execute(query, (ip_period,))

  # 提交事务
  mydb.commit()
  # 关闭连接
  mycursor.close()
  mydb.close()
  return True


def port_period_select():
  mydb,mycursor = connect_db()
  '''2.1、查询端口跳变周期'''
  mycursor.execute("SELECT * FROM app_settings WHERE name = 'port_change_period'")
  # 获取所有查询结果
  port_result = mycursor.fetchall()
  port_data_json = {
    "defense_id": "active_defense_subsystem",
    "name": "地面网络系统主动防御策略",
    "sid_rev": "active_defense_subsystem",
    "execute_unit": ["Port_mutation"],#IP跳变周期
    "defend_parameter":{
      "second": 20, },
    "other":{
      "Time": "2024-5-18 15:12:18" #IP跳变发生时间
      }
  }
  port_data_json["defend_parameter"] ["second"] = port_result[0][4]
  port_data_json["other"]["Time"] = port_result[0][2].strftime("%Y-%m-%d %H:%M:%S")
  print(port_data_json)

  # 关闭连接
  mycursor.close()
  mydb.close()

  return port_data_json



def port_period_modify(port_change_period):
  mydb,mycursor = connect_db()
  '''2.2、端口跳变周期修改'''
  query = "UPDATE app_settings SET value = %s WHERE name = 'port_change_period';"
  mycursor.execute(query, (port_change_period,))

  # 提交事务
  mydb.commit()
  # 关闭连接
  mycursor.close()
  mydb.close()

  return "端口跳变周期修改成功"


def node_period_select():
  mydb,mycursor = connect_db()
  '''3、查询网络更新周期'''
  mycursor.execute("SELECT * FROM app_settings WHERE name = 'node_query_period'")
  # 获取所有查询结果
  node_result = mycursor.fetchall()
  node_data_json = {
    "defense_id": "active_defense_subsystem",
    "name": "地面网络系统主动防御策略",
    "sid_rev": "active_defense_subsystem ",
    "execute_unit": ["False_Network_Update"],#IP跳变周期
    "defend_parameter":{
      "second": 20, },
    "other":{
      "Time": "2024-5-18 15:12:18" #IP跳变发生时间
      }
  }
  node_data_json["defend_parameter"] ["second"] = node_result[0][4]
  node_data_json["other"]["Time"] = node_result[0][2].strftime("%Y-%m-%d %H:%M:%S")
  print(node_data_json)
  # 关闭连接
  mycursor.close()
  mydb.close()

  return node_data_json

def node_period_modify(node_change_period):
  print(node_change_period)
  mydb,mycursor = connect_db()
  '''3、查询网络更新周期'''
  query = "UPDATE app_settings SET value = %s WHERE name = 'node_query_period';"
  mycursor.execute(query, (node_change_period,))
  mydb.commit()
  # 关闭连接
  mycursor.close()
  mydb.close()

  return mysql


def network_topology_select():
  mydb, mycursor = connect_db()
  mycursor.execute("SELECT * FROM app_settings WHERE name = 'ip_change_period'")
  # 获取所有查询结果
  ip_result = mycursor.fetchall()

  mycursor.execute("SELECT * FROM app_settings WHERE name = 'port_change_period'")
  # 获取所有查询结果
  port_result = mycursor.fetchall()

  '''4、查询网络拓扑'''
  mycursor.execute("SELECT * FROM net_nodes WHERE status = 0")
  # 获取所有查询结果
  network_topology_result = mycursor.fetchall()
  print(network_topology_result)

  network_topology = {
      "IP_mutation_Period": 10, #十进制数值
      "Port_mutation_Period": 20, #十进制数值
      "True-network-IP-List": { #字符串列表
      # "True-network-IP1 ": "192.168.11.2",
      # "True-network-IP2 ": "192.168.11.3",
      # "True-network-IP3 ": "192.168.11.4",
      # "True-network-IP4 ": "192.168.11.5",
      },
      "False-network-IP-List": {#字符串列表
      # "False-network-IP1 ": "192.168.12.2",
      # "False-network-IP2 ": "192.168.12.3",
      # "False-network-IP3 ": "192.168.12.4",
      # "False-network-IP4 ": "192.168.12.5",
    },
  }

  network_topology["IP_mutation_Period"] = ip_result[0][4]
  network_topology["Port_mutation_Period"] = port_result[0][4]

  count_nodes = len(network_topology_result)
  n = 1
  for i in range(count_nodes):
    if network_topology_result[i][4]=='10.2.87.253':
      continue
    if network_topology_result[i][7]=='honeypot':
      continue
    network_topology["True-network-IP-List"]["True-network-IP"+str(n)] = network_topology_result[i][4]
    network_topology["False-network-IP-List"]["False-network-IP" + str(n)] = network_topology_result[i][-1]
    n = n +1

  print(network_topology)
  # 关闭连接
  mycursor.close()
  mydb.close()

  return network_topology








