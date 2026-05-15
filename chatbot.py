from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Initialize model
model = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.9
    
)

print("choose your AI Mode")
print("press 1 for funny mode")
print("press 2 for sad mode")
print("press 3 for angry mode")

choice=int(input("Enter your choice : "))

if choice==1:
    mode="you are a funny AI assistant and reply every message in funny way ."
elif choice==2:
    mode="you are a sad AI assistant and reply every message in sad way ."
elif choice==3:
    mode="you are an angry AI assistant and reply every message in angry way ."


# Initialize messages

messages=[
    SystemMessage(content=mode)
]
print("____________________________WELCOME TYPE 0 TO EXIT____________________________")
while True:
    
    prompt=input("You : ")
    messages.append(HumanMessage(content=prompt))

    if prompt==0:
        print("Exiting...")
        break
   
    response = model.invoke(messages)
    messages.append(AIMessage(content=response.content))

    # Print response
    print("Bot :",response.content)

print(messages)