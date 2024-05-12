from flask import Flask, jsonify, request
from main import *

app = Flask(__name__)

print(response("내 이름이 뭐야"))

# app에서 질문을 요청 받아 답변 응답
@app.route('/giveInform')
def information():
    question = request.args.get('question')
    answer = response(question)
    data = {'answerofAI': answer}
    return jsonify(data)

#app에서 요청을 받으면 질문 생성
@app.route('/questionofAI')
def questioning():
    question = generate_question()
    data = {'questionofAI': question}
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")