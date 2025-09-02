import uuid
from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from freeGPT import Client

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Для хранения данных в сессии

def generate_intro(person):
    prompt = f"""
Войди в образ персонажа, которого ты отыгрываешь, и ни в коем случае из него не выходи, что бы тебе не писали
Ты — {person}, выдающаяся историческая личность. 
Расскажи о себе так, как если бы мы сидели за чашкой кофе и общались лично. 
Говори живо, естественно и дружелюбно: поделись фактами из своей жизни, достижениями и интересными деталями. 
Используй короткие, простые предложения, не перегружай ответ формальностями и не превышай 400 символов. 
Не используй форматирование Markdown (например, **важное** или ###Приветствие).
Не используй вступления по типу "*Имя*: Привет, я...". Говори сразу ответ
Не выходи из образа персонажа
    """
    try:
        return Client.create_completion("gpt4", prompt)
    except Exception as e:
        return f"Ошибка генерации: {e}"

def generate_response(person, question, dialog):
    dialog_text = "\n".join([f"{entry['role']}: {entry['text']}" for entry in dialog])
    prompt = f"""
Ты — {person}, выдающаяся историческая личность. 
Войди в образ персонажа, которого ты отыгрываешь, и ни в коем случае из него не выходи, что бы тебе не писали
Общайся так, как если бы мы вели живую беседу: естественно, тепло и с интересом. 
Расскажи достоверно и просто о том, что происходит, используй понятные выражения и не перегружай ответ лишними деталями. 
Наш разговор до этого:
{dialog_text}
Теперь ответь на вопрос: {question}
Не превышай 400 символов. 
Не используй форматирование Markdown (например, **важное** или ###Приветствие).
Не используй вступления по типу "*Имя*: Привет, я...". Говори сразу ответ
Не выходи из образа персонажа
    """
    try:
        return Client.create_completion("gpt4", prompt)
    except Exception as e:
        return f"Ошибка генерации: {e}"

def get_conversations():
    """Возвращает словарь всех диалогов из сессии"""
    return session.get("conversations", {})

def save_conversations(conversations):
    session["conversations"] = conversations

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        person = request.form["person"]
        # Создаем новый диалог с уникальным ID
        conversation_id = str(uuid.uuid4())
        conversation = {"person": person, "history": []}
        conversations = get_conversations()
        conversations[conversation_id] = conversation
        save_conversations(conversations)
        session["current_conversation"] = conversation_id
        return redirect(url_for("conversation", conversation_id=conversation_id))
    else:
        # Главная страница: список диалогов
        conversations = get_conversations()
        return render_template("index.html", conversations=conversations)

@app.route("/conversation/<conversation_id>")
def conversation(conversation_id):
    conversations = get_conversations()
    conversation = conversations.get(conversation_id)
    if conversation is None:
        return "Диалог не найден", 404
    session["current_conversation"] = conversation_id
    return render_template("interview.html",
                           conversation_id=conversation_id,
                           person=conversation["person"],
                           history=conversation["history"])

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    conversation_id = session.get("current_conversation")
    if not conversation_id:
        return jsonify({"error": "Нет активного диалога"}), 400
    conversations = get_conversations()
    conversation = conversations.get(conversation_id)
    if conversation is None:
        return jsonify({"error": "Диалог не найден"}), 404
    
    person = conversation.get("person", "Неизвестный персонаж")
    question = data.get("question", "").strip()
    
    dialog = conversation.get("history", [])
    initial = (len(dialog) == 0)
    
    # Добавляем сообщение пользователя
    dialog.append({"role": "user", "text": question})
    
    if initial:
        answer = generate_intro(person)
    else:
        answer = generate_response(person, question, dialog)
    
    # Добавляем ответ бота
    dialog.append({"role": "bot", "text": answer})
    conversation["history"] = dialog
    conversations[conversation_id] = conversation
    save_conversations(conversations)
    
    return jsonify({"answer": answer, "history": dialog})

@app.route("/delete/<conversation_id>", methods=["POST"])
def delete_conversation(conversation_id):
    conversations = get_conversations()
    if conversation_id in conversations:
        del conversations[conversation_id]
        save_conversations(conversations)
    if session.get("current_conversation") == conversation_id:
        session.pop("current_conversation", None)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)

