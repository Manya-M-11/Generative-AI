from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq

class Movie(BaseModel):#scheme
    name: str #which type of data you want to extract from the paragraph
    genre: List[str]
    release_date: Optional[int]
    director: Optional[str]
    cast: Optional[List[str]]


parser = PydanticOutputParser(pydantic_object=Movie)

model= ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.9
)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     '''extract movie information from the given paragraph.
     {format_instructions}'''),
     ("human",
     "{paragraph}"
     )
]
)


para=input("Give Your Paragraph : ")

final_prompt = prompt.invoke(
    {"paragraph": para,
     "format_instructions": parser.get_format_instructions()}
)



response=model.invoke(final_prompt)

print(response.content)