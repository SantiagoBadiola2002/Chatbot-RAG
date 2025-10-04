from services.chatbot import hybrid_chatbot

if __name__ == "__main__":
    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            break
        respuesta = hybrid_chatbot(user_input, session_id="user1")
        print(f"Bot: {respuesta}")
