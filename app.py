from flask import Flask, jsonify, send_from_directory, request
import slack_exporter
import llm

api_base_path = '/api/v1'
ds_dir = './datasets'

app = Flask(__name__)

@app.after_request
# adds no-cache headers to all responses
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route(f'{api_base_path}/slack/<channel>', methods=['POST'])
def dump_slack_channel(channel):
    try:
        se = slack_exporter.SlackExporter(channel)
        se.dump_channel()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route(f'{api_base_path}/dataset/<channel>', methods=['POST', 'GET'])
def create_dataset(channel):
    if request.method == 'GET':
        return send_from_directory(ds_dir, f'dataset.{channel}.json')

    try:
        m = llm.tierOneModel(channel)
        m.prepare_dataset()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
