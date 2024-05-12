import os 
from openai import OpenAI

### GPT
api_key = '{openai_key}'

client = OpenAI(
    api_key = api_key
)

# chat_completion = client.chat.completions.create(
#     messages=[{"role": "system", "content": "You are an intelligent assistant."},
#                   {"role": "user", "content": question},
#                   {"role": "assistant", "content": result}],
#     model="gpt-4"
# )

### 임베딩 모델
oepnai_embedding_model = "text-embedding-ada-002"

def get_embedding(text):
    result = client.embeddings.create(
        model=oepnai_embedding_model,
        input=text)
    return result.data[0].embedding


#### 데이터베이스 - pinecone
from pinecone import Pinecone

pc = Pinecone(api_key="254aa3fa-d6a3-4324-9376-50d859608601")
index = pc.Index("note")

# inform = "제 이름은 Seo Young-woo이고, 성별은 Female이며, 생년월일은 2003-10-07입니다."
# health = "저는 Chronic disease or allergy가 있으며, 의료 기록에는 medical history와 부모님이 수술을 받았는지 여부와 시기에 대한 세부 정보가 포함되어 있습니다."
# family = "저의 3촌 이내의 가족 관계는 Survival으로 기록되어 있습니다."

# inform_value = get_embedding(inform)
# health_value = get_embedding(health)
# family_value = get_embedding(family)

# index.upsert(
#   vectors=[
#     {"id": "A", "values": inform_value, "metadata":{"genre":"docs", "desc": inform}},
#     {"id": "B", "values": health_value, "metadata":{"genre":"docs", "desc": health}},
#     {"id": "C", "values": family_value, "metadata":{"genre":"docs", "desc": family}}
#     #{"id": "Phone", "values": [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]}
#   ],
#   namespace="user1"
# )

### 사용자가 질문하면 AI가 대답
user_input = input("입력 : ")


# 검색 함수
def retriever(user_input):
    question_embedding = get_embedding(user_input)
    result = index.query(
                namespace="user1",
                vector=question_embedding,
                filter={
                    "genre": {"$eq":"docs"}
                },
                top_k=3,
                include_metadata=True
            )
    prompt = f"""
    You are an intelligent assistant helping the users with their questions on {{company | research papers | …}}. Strictly Use ONLY the following pieces of context to answer the question at the end. Think step-by-step and then answer.
    The instructions should be in Korean. Reply via text only.

    Do not try to make up an answer:
     - If the answer to the question cannot be determined from the context alone, say "준비중입니다."
     - If the context is empty, just say "I do not know the answer to that."
 
    CONTEXT: 
    {result}
 
    QUESTION:
    {user_input}
     
    Strictly Use ONLY the following pieces of context to answer the question at the end.
    Helpful Answer:
    """
    return prompt

#print(retriever(user_input))

# 응답 함수
def response(question):
    messages = []
    messages.append({"role": "user", "content": question})

    result = retriever(question)

    chat_completion = client.chat.completions.create(
        messages=[{"role": "system", "content": "You are an intelligent assistant."},
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": result}],
        model="gpt-4"
    )

    message = chat_completion.choices[0].message.content
    return message

#print(response(user_input))



### AI가 질문하면 사용자가 대답
import numpy as np
# 질문 함수
def generate_question():
    messages = []

    result = index.query(
        namespace="user1",
        include_metadata=True,
        top_k=3,
        filter={
                    "genre": {"$eq":"docs"}
                },
        vector = np.random.rand(1536).tolist()
    )

    prompt = f"""
    You are an intelligent assistant making question with user's information. Strictly Use ONLY the following pieces of context to answer the question at the end. Think step-by-step and then make question about user.
    The instructions should be in Korean. Reply via text only.

    CONTEXT: 
    {result}
     
    Strictly Use ONLY the following pieces of context to make the question at the end.
    Make only ONE question.please
    Making Answer:
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "system", "content": "You are an intelligent assistant."},
                    #{"role": "user", "content": user_input},
                    {"role": "assistant", "content": prompt}],
        model="gpt-4"
    )

    message = chat_completion.choices[0].message.content
    return message

ai_question = generate_question()
print(ai_question)