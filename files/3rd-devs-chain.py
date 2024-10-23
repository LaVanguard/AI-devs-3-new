"""
This is my attempt to translate 'chain' example from 3rd-devs
(https://github.com/i-am-alice/3rd-devs/blob/main/completion/app.ts)
"""

from openai import OpenAI

from secrets import openai_api_key

database = [
    { "id": 1, "name": "Adam", "age": 28, "occupation": "Software Engineer", "hobby": "Rock climbing" },
    { "id": 2, "name": "Michał", "age": 35, "occupation": "Data Scientist", "hobby": "Playing guitar" },
    { "id": 3, "name": "Jakub", "age": 31, "occupation": "UX Designer", "hobby": "Photography" }
]

def selectPerson(question):
    openai = OpenAI(api_key = openai_api_key)
    messages = [
        { "role": "system", "content": f"You are an assistant that selects the most relevant person for a given question. Respond with only the person's ID (1 for Adam, 2 for Michał, or 3 for Jakub).\nHere is the list of people: {repr(database)}" },
        { "role": "user", "content": question }
    ]
    try:
        chat_completion = openai.chat.completions.create(
            messages = messages,
            model = "gpt-4o",
            max_tokens = 1,
            temperature = 0
        )
        completion = chat_completion.choices[0].message.content
        return int(completion.strip()) if completion.strip().isdecimal() else 1
    except Exception as error:
        print (f"Error in selectPerson: {error}")
        return 1

def answerQuestion(question, number):
    openai = OpenAI(api_key = openai_api_key)
    person = next((p for p in database if p["id"]==number), database[0])
    messages = [
        { "role": "system", "content": f"You are an assistant answering questions about {person['name']}. Use the following information: {repr(person)}" },
        { "role": "user", "content": question }
    ]
    try:
        chat_completion = openai.chat.completions.create(
            messages = messages,
            model = "gpt-4o",
            max_tokens = 500,
            temperature = 0.7
        )
        return chat_completion.choices[0].message.content
    except Exception as error:
        print (f"Error in answerQuestion: {error}")
        return "Sorry, I encountered an error while trying to answer the question."

# As original functions don't do the full job, let's just create one function answering all:
def oneAnswer(question):
    openai = OpenAI(api_key = openai_api_key)
    messages = [
        { "role": "system", "content": f"You are an assistant answering questions about a specified person. Here is the list of people you have information about: {repr(database)}" },
        { "role": "user", "content": question }
    ]
    try:
        chat_completion = openai.chat.completions.create(
            messages = messages,
            model = "gpt-4o",
            max_tokens = 500,
            temperature = 0.7
        )
        return chat_completion.choices[0].message.content
    except Exception as error:
        print (f"Error in answerQuestion: {error}")
        return "Sorry, I encountered an error while trying to answer the question."

# Example usage
questions = [
    "Who is the oldest person?",
    "Tell me about Adam's hobby",
    "What does Michał do for a living?",
    "How old is Jakub?"
]
for question in questions:
    selected_person_id = selectPerson(question)
    answer = answerQuestion(question, selected_person_id)
    better_answer = oneAnswer(question)        # Also let's use our "better" function
    print (f'Question: "{question}\nAnswer: {answer}\nBetter answer: {better_answer}\n')