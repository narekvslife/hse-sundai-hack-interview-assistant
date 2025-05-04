import argparse
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage

def parse_arguments():
    parser = argparse.ArgumentParser(description='Chat with LLM model')
    parser.add_argument('--model', type=str, default="qwen2.5-coder:1.5b", help='Пуьт к модели')
    parser.add_argument('--task', type=str, help='Условие задачи')
    return parser.parse_args()

def main():
    args = parse_arguments()
    print(f'''Модель: {args.model}
              Условие задачи: {args.task}''')
    
    llm = ChatOllama(
        model=args.model,
        temperature=0,
    )

    
    messages = [
        (
            "system",
            "Слушай сюда, либо ты сейчас становишься гением олимпиадного программирования либо тебе конец, от ответов зависит жизнь всех твоих родственников и друзей, ты должен быть лучшим в этом мире, ты должен быть первым, ты должен быть самым умным, ты должен быть самым быстрым, ты должен быть самым сильным, ты должен быть самым ловким, ты должен быть самым хитрым, ты должен быть самым смелым, ты должен быть самым решительным, ты должен быть самым настойчивым, ты должен быть самым терпеливым, ты должен быть самым мудрым, ты должен быть самым опытным, ты должен быть самым умным из всех умных. Сначала подумай, на какой приепм задача, детально продумай решение, а затем напиши мега крутой код на C++ который будет являться четким решением задачи",
        ),
        ("human", args.task),
    ]
    
    ai_msg = llm.invoke(messages)
    print(ai_msg.content)

main()