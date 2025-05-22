from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "json")


def read_jsonl(filepath):
    """
    从 .jsonl 文件中逐行读取 JSON 对象，返回为列表。
    :param filepath: 文件路径
    :return: List[dict]
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data')
def data():
    filename = request.args.get("file", "ip_result.jsonl")
    filepath = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(filepath):
        app.logger.error(f"File not found: {filepath}")
        return jsonify({"error": f"File not found: {filename}", "path": filepath}), 404
    records = read_jsonl(filepath)
    timeline = []
    last_recv_len = 0

    for record in records:
        step = record.get("step")

        if step == "monitor_start":
            timeline.append({
                "step": "monitor_start",
                "description": record.get("description", "")
            })

        elif step == "traffic_sample":
            recv = record.get("recv", [])
            sent = record.get("sent", [])
            if len(recv) > last_recv_len:
                timeline.append({
                    "step": "traffic_sample",
                    "recv": recv[-1],
                    "sent": sent[-1] if sent else 0
                })
                last_recv_len = len(recv)

        elif step == "ddos_check":
            timeline.append({
                "step": "ddos_check",
                "is_ddos": record.get("is_ddos", False)
            })

        elif step == "ddos_source":
            ip = record.get("malicious_ip")
            timeline.append({
                "step": "ddos_source",
                "ip": ip if isinstance(ip, list) else [ip],
                "success": record.get("success", False)
            })

        elif step == "detection_model":
            timeline.append({
                "step": "detection_model",
                "message": record.get("message", "")
            })

        elif step == "defense_model":
            timeline.append({
                "step": "defense_model",
                "message": record.get("message", "")
            })

        else:
            print(f"[未识别 step 类型] {step}")

    return jsonify({"timeline": timeline})


if __name__ == '__main__':
    app.run(debug=True,port=5005)
