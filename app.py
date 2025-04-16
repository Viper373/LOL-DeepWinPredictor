import pymysql
import numpy as np
from flask import Flask, request, jsonify, render_template
import json
import torch
import logging
from BILSTM_Att.BILSTM_Att import BiLSTMModelWithAttention

app = Flask(__name__)

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义常量
DATA_DIR = 'data/json/'
MODEL_PATH = 'static/saved_model/BILSTM_Att.pt'
HERO_INFO_FILE = 'hero_info.json'
HERO_WIN_RATE_FILE = 'hero_win_rate.json'
TEAM_LIST_FILE = 'team_list.json'

# 加载英雄和队伍数据（添加异常处理）
try:
    with open(DATA_DIR + HERO_INFO_FILE, 'r', encoding='utf-8') as f:
        hero_list = json.load(f)
    with open(DATA_DIR + HERO_WIN_RATE_FILE, 'r', encoding='utf-8') as f:
        hero_win_rate = json.load(f)
    with open(DATA_DIR + TEAM_LIST_FILE, 'r', encoding='utf-8') as f:
        team_list = json.load(f)
except FileNotFoundError as e:
    logger.error(f"文件不存在错误: {e}")
    hero_list, hero_win_rate, team_list = [], {}, {}  # 设置为默认值或采取其他适当的错误处理措施

# 加载LSTM模型（添加异常处理）
try:
    model = BiLSTMModelWithAttention(input_size=32, hidden_size=1024, num_layers=2, output_size=1)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))  # 确保在CPU上加载
    model.eval()
except Exception as e:
    logger.error(f"模型加载错误: {e}")
    model = None  # 设置为默认值或采取其他适当的错误处理措施


# Flask路由
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '').lower()
    suggestions = [hero for hero in hero_list if query in hero['name'].lower()]
    return jsonify(suggestions)


@app.route('/query_hero', methods=['GET'])
def query_hero():
    return jsonify(hero_list)


@app.route('/query_win_rate', methods=['GET'])
def query_win_rate():
    return jsonify(hero_win_rate)


@app.route('/query_team', methods=['GET'])
def query_team():
    query = request.args.get('query', '').lower()
    suggestions = {}
    for team_id, team in team_list.get("data", {}).items():
        if query in team['TeamName'].lower() or query in team['TeamShortName'].lower():
            suggestions.update({team_id: team})
    return jsonify(suggestions)


@app.route('/get_echarts_data', methods=['GET'])
def get_heroes_data():
    # 连接MySQL数据库
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='ShadowZed666',
        database='lol'
    )
    cursor = conn.cursor()

    # 获取数据
    cursor.execute('SELECT hero_id, hero_name, TOP, JUN, MID, ADC, SUP FROM hero_win_rates')
    rows = cursor.fetchall()

    # 关闭连接
    cursor.close()
    conn.close()

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
        hero_id = row[0]
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
    try:
        data = request.json
        print(data)
        # 为模型准备输入数据
        input_data = np.array([[
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
        ]])

        # 转换为张量
        input_tensor = torch.Tensor(input_data).reshape(1, 1, -1)

        # 进行预测
        with torch.no_grad():
            prediction = model(input_tensor).item()

        # 获胜队伍的信息
        winning_team_id = data['left_team']['teamAid'] if prediction > 0.5 else data['right_team']['teamBid']
        winning_team = team_list.get('data').get(str(winning_team_id))

        response = {
            'A_win': prediction * 100,
            'B_win': (1 - prediction) * 100,
            'winning_team': {
                'name': winning_team['TeamName'],
                'logo': winning_team['TeamLogo']
            }
        }

        return jsonify(response)
    except Exception as e:
        # 对于POST请求的异常处理，返回400 Bad Request和错误信息
        logger.error(f"预测错误: {e}")
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)


