import json
import os

import numpy as np
import torch
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from BILSTM_Att.BILSTM_Att import BiLSTMModelWithAttention
from Data_CrawlProcess import env
from tool_utils.log_utils import RichLogger
from tool_utils.mysql_utils import MySQLUtils

rich_logger = RichLogger()
mysql_utils = MySQLUtils()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)

# ================== 数据加载 ==================
# 加载英雄和队伍数据（添加异常处理）
try:
    with open(env.HERO_INFO, 'r', encoding='utf-8') as f:
        hero_list = json.load(f)
    with open(env.HERO_WIN_RATE, 'r', encoding='utf-8') as f:
        hero_win_rate = json.load(f)
    with open(env.TEAM_LIST, 'r', encoding='utf-8') as f:
        team_list = json.load(f)
except FileNotFoundError as e:
    rich_logger.error(f"文件不存在错误: {e}")
    hero_list, hero_win_rate, team_list = [], [], []

# 加载LSTM模型（添加异常处理）
try:
    model = BiLSTMModelWithAttention(input_size=32, hidden_size=1024, num_layers=2, output_size=1)
    """
    加载模型权重
    :param MODEL_PATH: 模型文件路径
    :return: None
    """
    model.load_state_dict(torch.load(env.MODEL_PATH, map_location=torch.device('cpu'), weights_only=True))  # 确保在CPU上加载，且只加载权重
    model.eval()
except Exception as e:
    rich_logger.error(f"模型加载错误: {e}")
    model = None  # 设置为默认值或采取其他适当的错误处理措施


# ================== 路由定义 ==================
@app.route('/')
def index():
    """
    首页渲染，并统计访问
    """
    ip = request.remote_addr
    mysql_utils.record_visit(ip)
    return render_template('index.html')


@app.route('/site_stats', methods=['GET'])
def site_stats():
    """
    获取站点访问次数和访问人数
    :return: JSON {visit_count, visitor_count}
    """
    total, user = mysql_utils.get_site_stats()
    return jsonify({
        "visit_count": total,
        "visitor_count": user
    })


@app.route('/query_hero', methods=['GET'])
def query_hero():
    """
    获取英雄列表
    :return: 英雄列表JSON
    """
    return jsonify(hero_list)


@app.route('/query_win_rate', methods=['GET'])
def query_win_rate():
    """
    获取英雄胜率数据
    :return: 英雄胜率JSON
    """
    return jsonify(hero_win_rate)


@app.route('/query_team', methods=['GET'])
def query_team():
    """
    查询队伍信息，直接返回所有队伍数组，便于前端自动补全。
    :return: 队伍列表
    """
    data = team_list.get("data", team_list) if isinstance(team_list, dict) else team_list
    return jsonify(data)


@app.route('/get_echarts_data', methods=['GET'])
def get_heroes_data():
    """
    获取MySQL中的英雄分路胜率数据，供前端Echarts使用
    :return: 英雄分路胜率字典
    """
    rows = mysql_utils.select_hero_win_rate()
    # 解析数据
    heroes_data = {
        0: {
            'name': 'None',
            'top': 0,
            'jun': 0,
            'mid': 0,
            'adc': 0,
            'sup': 0,
        }
    }
    for row in rows:
        hero_id = int(row[0])
        hero_name = row[1]
        heroes_data[hero_id] = {
            'name': hero_name,
            'top': row[2],
            'jun': row[3],
            'mid': row[4],
            'adc': row[5],
            'sup': row[6],
        }
    return jsonify(heroes_data)


@app.route('/predict', methods=['POST'])
def predict():
    """
    预测比赛胜率接口
    :return: 预测结果JSON
    """
    try:
        data = request.json
        # 为模型准备输入数据
        input_data = np.array([
            [
                data['left_team']['teamAid'], data['right_team']['teamBid'],
                data['left_team']['A1playerLocation'], data['left_team']['A1heroId'], data['left_team']['A1heroWinRate'],
                data['left_team']['A2playerLocation'], data['left_team']['A2heroId'], data['left_team']['A2heroWinRate'],
                data['left_team']['A3playerLocation'], data['left_team']['A3heroId'], data['left_team']['A3heroWinRate'],
                data['left_team']['A4playerLocation'], data['left_team']['A4heroId'], data['left_team']['A4heroWinRate'],
                data['left_team']['A5playerLocation'], data['left_team']['A5heroId'], data['left_team']['A5heroWinRate'],
                data['right_team']['B1playerLocation'], data['right_team']['B1heroId'], data['right_team']['B1heroWinRate'],
                data['right_team']['B2playerLocation'], data['right_team']['B2heroId'], data['right_team']['B2heroWinRate'],
                data['right_team']['B3playerLocation'], data['right_team']['B3heroId'], data['right_team']['B3heroWinRate'],
                data['right_team']['B4playerLocation'], data['right_team']['B4heroId'], data['right_team']['B4heroWinRate'],
                data['right_team']['B5playerLocation'], data['right_team']['B5heroId'], data['right_team']['B5heroWinRate']
            ]
        ])

        # 转换为张量
        input_tensor = torch.Tensor(input_data).reshape(1, 1, -1)

        # 进行预测
        with torch.no_grad():
            prediction = model(input_tensor).item()

        # 获胜队伍的信息
        winning_team_id = data['left_team']['teamAid'] if prediction > 0.5 else data['right_team']['teamBid']
        # 兼容 team_list 为 dict 或 list
        if isinstance(team_list, dict):
            team_data = team_list.get('data', team_list)
        else:
            team_data = team_list
        winning_team = None
        if isinstance(team_data, dict):
            winning_team = team_data.get(str(winning_team_id)) or team_data.get(winning_team_id)
        elif isinstance(team_data, list):
            for t in team_data:
                if str(t.get('teamId')) == str(winning_team_id):
                    winning_team = t
                    break
        if not winning_team:
            raise Exception(f"未找到获胜队伍信息: {winning_team_id}")

        response = {
            'A_win': prediction * 100,
            'B_win': (1 - prediction) * 100,
            'winning_team': {
                'name': winning_team['teamName'],
                'logo': winning_team['teamLogo']
            }
        }
        return jsonify(response)
    except Exception as e:
        rich_logger.error(f"预测错误: {e}")
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run()
