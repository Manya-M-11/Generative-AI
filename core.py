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
     '''You are an intelligent movie information extraction assistant.

Your task is to read the given movie paragraph carefully and extract the most useful movie-related information.

Instructions:
- Identify the movie name.
- Identify the genre of the movie.
- Identify the main characters or cast mentioned.
- Identify the director if mentioned.
- Identify the release date if mentioned.
- Identify the language if mentioned.
- Extract important keywords and themes from the paragraph.
- Generate a short and meaningful summary in 2-3 lines.
- If any information is not available in the paragraph, simply write "Not Available".
- Keep the response clean, structured, and easy to read.

Movie Paragraph:
{movie_paragraph}

Output Format:

Movie Name:
Genre:
Release Date:
Director:
Cast / Characters:
Language:
Main Themes:
Important Keywords:
Quick Summary:'''

),
("human",
 '''Extarct the information and summary from the following movie paragraph: 
 {movie_paragraph}'''
)
]
)

para=input("Give Your Paragraph : ")

final_prompt = prompt.invoke(
    {"movie_paragraph": para}
)



response=model.invoke(final_prompt)

print(response.content)