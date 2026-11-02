import os
import json
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from agent.tools import all_tools

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AIAgent")

class AIAgent:
    def __init__(self, memory_file="memory.json"):
        self.memory_file = memory_file
        logger.info("Инициализация LLM (gpt-4) через ProxyAPI...")
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0, 
            base_url=os.getenv("OPENAI_BASE_URL")
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Ты — полезный локальный AI-Агент. Ты можешь использовать инструменты для выполнения задач. "
                       "Отвечай кратко, четко и по делу. Если не хватает данных — переспроси пользователя."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        logger.info("Сборка агента с инструментами...")
        # Используем современный create_react_agent из langgraph
        self.executor = create_react_agent(self.llm, all_tools)

    def load_memory(self):
        if os.path.exists(self.memory_file):
            logger.info(f"Загрузка памяти из {self.memory_file}")
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                try:
                    history = json.load(f)
                    return [self._parse_message(m) for m in history]
                except Exception as e:
                    logger.error(f"Ошибка загрузки памяти: {e}")
                    return []
        return []

    def save_memory(self, history):
        logger.info(f"Сохранение памяти в {self.memory_file}")
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump([self._message_to_dict(m) for m in history], f, ensure_ascii=False, indent=2)

    def _parse_message(self, m):
        if m["role"] == "user": return HumanMessage(content=m["content"])
        return AIMessage(content=m["content"])

    def _message_to_dict(self, m):
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        return {"role": role, "content": m.content}

    def run(self, user_input: str):
        logger.info(f"Пользователь: {user_input}")
        history = self.load_memory()
        
        try:
            # LangGraph агенты принимают состояние в виде словаря с ключом "messages"
            inputs = {"messages": history + [HumanMessage(content=user_input)]}
            response = self.executor.invoke(inputs)
            
            # Последнее сообщение в списке сообщений будет ответом агента
            output = response["messages"][-1].content
            logger.info(f"Агент ответил: {output}")
        except Exception as e:
            logger.error(f"Критическая ошибка при выполнении: {e}", exc_info=True)
            return f"Произошла ошибка: {e}"
        
        history.append(HumanMessage(content=user_input))
        history.append(AIMessage(content=output))
        self.save_memory(history)
        
        return output
