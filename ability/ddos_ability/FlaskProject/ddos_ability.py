from flask import Flask, render_template, request, jsonify
import json
import os


DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "json")


class DdosAbility:
    def __init__(self):
        pass

    def read_jsonl(self,filepath):
        """
        从.jsonl文件中逐行读取JSON对象
        :param filepath: 文件路径
        :return: 包含所有JSON记录的列表
        """
        records = []
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue  # 跳过空行
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"[第 {i} 行解析失败] {e} | 内容: {line}")
        return records

    def data(self,filename):
        filepath = os.path.join(DATA_FOLDER, filename)

        # 文件不存在处理
        if not os.path.exists(filepath):
            return jsonify({"error": f"File not found: {filename}", "path": filepath}), "fail"  # 失败返回 "fail" 状态字和错误信息

        records = self.read_jsonl(filepath)
        timeline = []  # 时间线数据容器
        last_recv_len = 0  # 记录上次接收数据长度

        # 解析每条监控记录
        for record in records:
            step = record.get("step")

            # 监控开始事件
            if step == "monitor_start":
                timeline.append({
                    "step": "monitor_start",
                    "description": record.get("description", "")
                })

            # 流量采样数据
            elif step == "traffic_sample":
                recv = record.get("recv", [])
                sent = record.get("sent", [])
                profit = record.get("profit", [])
                if len(recv) > last_recv_len:  # 只记录新增数据点
                    timeline.append({
                        "step": "traffic_sample",
                        "recv": recv[-1],  # 取最新接收数据
                        "sent": sent[-1] if sent else 0,  # 取最新发送数据
                        "profit": profit if profit else []
                    })
                    last_recv_len = len(recv)

            # DDoS检测结果
            elif step == "ddos_check":
                timeline.append({
                    "step": "ddos_check",
                    "is_ddos": record.get("is_ddos", False)
                })

            # 攻击源定位结果
            elif step == "ddos_source":
                ip = record.get("malicious_ip")
                timeline.append({
                    "step": "ddos_source",
                    "ip": ip if isinstance(ip, list) else [ip],  # 统一转为列表格式
                    "success": record.get("success", False)
                })

            # 检测模型输出
            elif step == "detection_model":
                timeline.append({
                    "step": "detection_model",
                    "message": record.get("message", "")
                })

            # 防御模型输出
            elif step == "defense_model":
                timeline.append({
                    "step": "defense_model",
                    "message": record.get("message", "")
                })

            else:
                print(f"[未识别 step 类型] {step}")

        return jsonify({"timeline": timeline}), "success"  # 成功返回 "success" 状态字和时间线数据


