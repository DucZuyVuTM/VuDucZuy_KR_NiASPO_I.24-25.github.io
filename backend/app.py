import os
from flask import Flask, jsonify
from kafka import KafkaProducer
import pandas as pd
import logging
import pybreaker
import traceback
from sqlalchemy import create_engine, MetaData, Table, Column, Integer

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

circuit_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)

producer = KafkaProducer(bootstrap_servers=os.environ['KAFKA_BROKER'],
                         api_version=(0,11,5))

app = Flask(__name__)

# Cấu hình kết nối tới PostgreSQL
DATABASE_URI = 'postgresql://app_user:password@database:5432/covid19'
engine = create_engine(DATABASE_URI)
metadata = MetaData()

# Định nghĩa bảng dữ liệu
vietnam_table = Table(
    'vietnam_data', metadata,
    Column('day', Integer, primary_key=True, autoincrement=True),
    Column('confirmed', Integer, nullable=False),
    Column('recovered', Integer, nullable=False),
    Column('deaths', Integer, nullable=False)
)

# Tạo bảng nếu chưa tồn tại
metadata.create_all(engine)

# URL chứa dữ liệu
DATA_URL = 'https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv'

# Đọc dữ liệu từ URL và lọc cho Việt Nam
df = pd.read_csv(DATA_URL)
df_vietnam = df[df['Country'] == 'Vietnam']  # Cột 'Country' chứa tên quốc gia

@app.route('/health', methods=['GET'])
def health():
    return jsonify(status='healthy'), 200

@app.route('/data', methods=['GET'])
@circuit_breaker
def show_data():
    logging.info('Endpoint /data was called')
    return jsonify(df_vietnam.to_dict(orient='records'))

@app.route('/graph', methods=['POST'])
def graph():
    logging.info('Endpoint /graph was called')
    try:
        y1 = df_vietnam['Confirmed']
        y2 = df_vietnam['Recovered']
        y3 = df_vietnam['Deaths']
        x = list(range(1, len(y1) + 1))  # Bắt đầu từ 1 để phù hợp với mục đích phân tích

        logging.info(f"'x_values': {x}")
        logging.info(f"'y1_values': {y1.tolist()}")
        logging.info(f"'y2_values': {y2.tolist()}")
        logging.info(f"'y3_values': {y3.tolist()}")

        return jsonify({
            'x_values': x,
            'y1_values': y1.tolist(),
            'y2_values': y2.tolist(),
            'y3_values': y3.tolist(),
        })
    except Exception as e:
        # Ghi lại thông tin lỗi
        logging.error(f"Error in graph endpoint: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/send', methods=['GET', 'POST'])
@circuit_breaker
def send():
    logging.info('Endpoint /send was called')
    
    # Chuyển đổi DataFrame thành danh sách các dict
    records_to_send = df_vietnam.to_dict(orient='records')

    # Kết nối tới PostgreSQL
    with engine.connect() as connection:
        trans = connection.begin()  # Bắt đầu một transaction
        try:
            connection.execute(vietnam_table.delete())
            for idx, record in enumerate(records_to_send):
                connection.execute(vietnam_table.insert().values(
                    day=idx + 1,
                    confirmed=record['Confirmed'],
                    recovered=record['Recovered'],
                    deaths=record['Deaths']
                ))
            trans.commit()  # Commit thay đổi
        except:
            trans.rollback()  # Rollback nếu có lỗi
            raise

    return jsonify({"status": "All data sent to PostgreSQL", "count": len(records_to_send)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)