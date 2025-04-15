import json
from flask import Flask, jsonify
from flask_cors import CORS
from collections import OrderedDict

app = Flask(__name__)
CORS(app, origins='http://localhost:3000')

# 读取 JSON 文件并转换为所需格式


def load_chart_data(data_type):
    with open(f'{data_type}.json', 'r', encoding='utf-8') as file:
        raw_data = json.load(file)

    # 转换数据格式
    data_dict = OrderedDict({})
    for row in raw_data:
        key = row[0]  # 第一个元素作为键
        if key == "close_ma": # 不加载 close_ma 数据
            continue
        values = row[1:]  # 剩余元素作为值
        data_dict[key] = values

    return data_dict


# 加载数据
chart_data = {
    "signal": load_chart_data("signal"),
    "trend": load_chart_data("trend"),
    "scope": load_chart_data("scope"),
}


@app.route('/chart_data/<chart_type>/<k_time>', methods=['GET'])
def get_chart_data(chart_type, k_time):
    """
    返回图表数据
    """
    # 目标时间戳
    k_time = k_time or "20250411031900"

    data = chart_data[chart_type]

    # 找到小于目标时间戳的索引
    indices = [i for i, timestamp in enumerate(data["id"]) if timestamp <= k_time]

    # 提取数据
    result = OrderedDict({k: [v[i] for i in indices] for k, v in data.items()})

    option = {
        "legend": [k for k in result.keys() if k != "id"],
        "xAxis": result["id"],
        "series": [{"name": k, "data": v} for k, v in result.items() if k != "id"],
    }
    return jsonify(option)


@app.route('/next_data/<chart_type>/<k_time>', methods=['GET'])
def next_chart_data(chart_type, k_time):
    """
    返回 k_time 的下一个图表数据
    """
    # 尝试找到 k_time 在 id 列表中的索引
    try:
        data = chart_data[chart_type]
        index = data["id"].index(k_time)
        next_index = index + 1
        if (next_index >= len(data["id"])):
            return
        next_data = {
            "xAxis": data["id"][next_index],
            "series": [v[next_index] for k, v in data.items() if k != "id"]
        }
        return jsonify(next_data)
    except ValueError:
        return jsonify({"error": "Invalid k_time value"}), 400


if __name__ == '__main__':
    app.run(debug=True)
