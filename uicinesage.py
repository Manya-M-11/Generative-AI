import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
import json

# Load environment variables
load_dotenv()

# -----------------------------
# Pydantic Schema
# -----------------------------
class Movie(BaseModel):
    name: str
    genre: List[str]
    release_date: Optional[int]
    director: Optional[str]
    cast: Optional[List[str]]

# Parser
parser = PydanticOutputParser(pydantic_object=Movie)

# Model
model = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.9
)

# Prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
Extract movie information from the given paragraph.

{format_instructions}
"""
    ),
    (
        "human",
        "{paragraph}"
    )
])

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(
    page_title="Movie Information Extractor",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Movie Information Extractor")

st.write("Paste a movie paragraph below to extract useful information.")

# Text Area
paragraph = st.text_area(
    "Enter Movie Paragraph",
    height=250,
    placeholder="Paste movie description here..."
)

# Button
if st.button("Extract Information"):

    if paragraph.strip() == "":
        st.warning("Please enter a movie paragraph.")
    else:

        with st.spinner("Extracting information..."):

            # Create Prompt
            final_prompt = prompt.invoke({
                "paragraph": paragraph,
                "format_instructions": parser.get_format_instructions()
            })

            # Model Response
            response = model.invoke(final_prompt)

            # Parse Output
            parsed_output = parser.parse(response.content)

            # Convert to Dictionary
            movie_data = parsed_output.dict()

            # -----------------------------
            # Display Results
            # -----------------------------
            st.success("Information Extracted Successfully!")

            st.subheader("📌 Extracted Information")

            st.write(f"**Movie Name:** {movie_data['name']}")
            st.write(f"**Genre:** {', '.join(movie_data['genre'])}")

            st.write(f"**Release Date:** {movie_data['release_date']}")
            st.write(f"**Director:** {movie_data['director']}")

            if movie_data['cast']:
                st.write(f"**Cast:** {', '.join(movie_data['cast'])}")
            else:
                st.write("**Cast:** Not Available")

            # -----------------------------
            # JSON Display
            # -----------------------------
            st.subheader("📄 JSON Output")

            json_output = json.dumps(movie_data, indent=4)

            st.code(json_output, language="json")

            # -----------------------------
            # Download JSON
            # -----------------------------
            st.download_button(
                label="⬇ Download JSON File",
                data=json_output,
                file_name="movie_information.json",
                mime="application/json"
            )