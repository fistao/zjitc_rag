from flask import Flask, request, jsonify
import rag_service

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    answer = rag_service.generate_answer(question)
    return jsonify({"question": question, "answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)