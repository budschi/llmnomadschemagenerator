from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import sys
from nomad.client import parse, normalize_all
import yaml
import ast
import streamlit as st
import os
import traceback

llm = Ollama(model="llama3:70b")
llm.base_url = 'http://172.28.105.30/backend'

#eln_schema = llm.invoke(userprompt)
#please use this input to generate a yaml schema for the following input :

cheatsheet=    """
You are a schema generator. Below you will get a schema snippet as input. You should output only the generated schema and no other text!
here is a snippet from cheat sheet to write data schemas in yaml for NOMAD (www.nomad-lab.eu):
# Description: This is a cheat sheet for the NOMAD custom schema.
#   It is a minimal example of how to define a custom schema.
#   It is not intended to be used for real data.
#   It is intended to be used as a starting point for defining a custom schema.
#   It is intended to be used as a reference for the syntax of the custom schema.

# defining the schema:
definitions:
  name: "Cheatsheet"
  sections:
    CheatSheet: # sections are in pascal case (not mandatory but best practice)
      base_sections:
      - nomad.datamodel.data.EntryData

      # adding quantities:
      quantities: # quantities are in snake case (not mandatory but best practice)

        # myquantity: test
        string:
          type: string
          description:
          m_annotations:
            eln:
              component: StringEditQuantity

        # reference: www.example.com
        url_link:
          type: string
          description:
          m_annotations:
            eln:
              component: URLEditQuantity

        # myfloatquantity: 1.0
        float:
          type: np.float64
          description:
          m_annotations:
            eln:
              component: NumberEditQuantity

        # myfloatquantitywithunit: 1.0 fs
        float_unit:
          type: np.float64
          unit: second
          description:
          m_annotations:
            eln:
              component: NumberEditQuantity
              defaultDisplayUnit: "fs"

        # myfloatquantitywithderivedunit: 1.0 eV
        float_derived_unit:
          type: np.float64
          unit: joule
          description:
          m_annotations:
            eln:
              component: NumberEditQuantity
              defaultDisplayUnit: "eV"

        # myfloatquantitycomplexunit: 1.0 mA/ms^2*cm
        float_complex_unit:
          type: np.float64
          unit: ampere / second^2 * meter
          description:
          m_annotations:
            eln:
              component: NumberEditQuantity
              defaultDisplayUnit: "milliampere / ms^2 * cm"

        # myfloatquantitywithbounds: 0.0 - 10.0 m
        float_with_bounds:
          type: np.float64
          unit: meter
          description:
          m_annotations:
            eln:
              component: NumberEditQuantity
              minValue: 0
              maxValue: 10

        # myintquantity: 1
        int:
          type: int
          description:
          m_annotations:
            eln:
              component: NumberEditQuantity

        # myintquantitywithbounds: 0 - 10
        int_with_bounds:
          type: int
          description:
          m_annotations:
            eln:
              component: NumberEditQuantity
              minValue: 0
              maxValue: 10

        # myboolquantity: true
        bool:
          type: bool
          description:
          m_annotations:
            eln:
              component: BoolEditQuantity

Please use this input to generate a yaml schema for the following input and output only the generated schema in the chat:
"""

# with open('nomad_cheat_sheet.schema.archive.txt', 'r') as file:
#     content = file.read()
#     content.replace("`", "")
#     cheatsheet = "You are a schema generator. Below you will get a schema snippet as input. You should output only the generated schema and no other text!\n here is a snippet from cheat sheet to write data schemas in yaml for NOMAD (www.nomad-lab.eu):" + content + ("\n \n \nPlease use this input to generate a yaml schema for the following input and output only the generated schema in the chat:")

prompt = ChatPromptTemplate.from_template(cheatsheet + "{userpromp}")
output_parser = StrOutputParser()
chain = prompt | llm | output_parser



def invokechain(userinput):
  """Input text from user

  Parameters
  ----------
  userinput : str
  """
  return chain.invoke({"userpromp": userinput })

def convert_pdf_to_text(pdf_file):
   # Read the pdf

    pdf_file = "/home/rubel/Downloads/delete_2/papers/152101_1_online.pdf"


    from langchain_community.document_loaders import PyPDFLoader

    loader = PyPDFLoader(pdf_file)
    pages = loader.load_and_split()

    text = ""
    for page in pages:
        text += page.page_content

    text = text.encode('utf-8')
    return extract_experiment_info_from_text(text)

def extract_experiment_info_from_text(text):
  """
  Extract text from text file
  """
  cheatsheet=    """
You are a physical quantity extractor. Below you will get some data from a lab. You should output the lab and experiment information and no other text!
here is a snippet from cheat sheet to write information about a lab and experiment from a lab sheet:
# Description: This is a cheat sheet for experimental lab and user description.
#   It is a minimal example of how to a experiment and lab.
#   It is intended to be used as a starting point for definig a experiment and lab.

MyLabAndExperimentInfo:
  temperature: 394.5K
  process_finished: True
  user: Sebastian
"""

  prompt = ChatPromptTemplate.from_template(cheatsheet + "{userpromp}")
  output_parser = StrOutputParser()
  chain = prompt | llm | output_parser

  result = chain.invoke({"userpromp": text })
  return result
   
def get_user_input():
    counter = 0
    while counter < 5:
        user_input = st.text_area("Enter your description of your experiment here:")

        file = st.file_uploader("Please enter a file e.g. pdf, text")
        try:
            if os.path.isfile(file):
                if isinstance(user_input, str):
                    st.text("Please enter only one input either file or text.")
                    counter += 1
                    continue
                break
        except Exception as e:
            if isinstance(user_input, str):
                break
            counter += 1
            pass
                       
    try:
      if os.path.isfile(file):
        if file.endswith('.pdf'):
          user_input = convert_pdf_to_text(file)
          st.text(user_input)
          return user_input
    except Exception as e:
      if isinstance(user_input, str):
        return user_input
    else:
        raise ValueError("Please enter a valid input")


def run_llm(user_input, max_iter):
   if st.button('Generate Schema'):
    # Call the invokechain function with the user's input
    result = invokechain(user_input)
    #result = yaml.safe_load(ast.literal_eval(result))
    with open('output.schema.archive.yaml', 'w') as file:
        data = yaml.load(result, Loader=yaml.FullLoader)  # Use FullLoader to parse the YAML
        yaml.dump(data, file, default_flow_style=False) 
    #try:
    #    parse('output.schema.archive.yaml')
    #except Exception:
    #    error_message = traceback.format_exc()
    #    st.write(error_message)    
    counter=0
    error = None
    try:
        # Replace this with the actual parse command
        parse('output.schema.archive.yaml')
    except Exception as e:
        error = e
        st.write(counter)
        st.write(f"An error occurred: {error}")
    
        for counter in range(max_iter):
            counter += 1
            st.write(counter)
            result = invokechain("You produced the following schema:" + result + "\n It returned this error: " + str(error) + "Please fix the schema and try again.")
            #result = yaml.safe_load(ast.literal_eval(result))
            with open('output.schema.archive.yaml', 'w') as file:
                data = yaml.load(result, Loader=yaml.FullLoader)  # Use FullLoader to parse the YAML
                yaml.dump(data, file, default_flow_style=False) 
            #try:
            #    parse('output.schema.archive.yaml')
            #except Exception:
            #    error_message = traceback.format_exc()
            #    st.write(error_message)    
            error = None
            try:
                # Replace this with the actual parse command
                parse('output.schema.archive.yaml')
                break
            except Exception as e:
                error = e
                st.write(f"An error occurred: {error}")
        # Display the result
    st.markdown(f"```attempt result```: {counter}")

    st.text("``` \n" + result)

def download_schema():
  with open('output.schema.archive.yaml', 'r') as file:
      file_content = file.read()
  st.download_button(
      label="Download output.schema.archive.yaml",
      data=file_content,
      file_name="output.schema.archive.yaml",
      mime="application/x-yaml"
)

def init_app():
    # Title of the app
    st.title('NOMAD Schema Generator App')
    appdescription="""
    This Generator App can create Custom yaml schemas for NOMAD (www.nomad-lab.eu).
    It takes the user prompt, generates a yaml schema and prints it below if it 
    was verified successfully to be a working NOMAD schema. 
    In case the LLM generates errors it will try to fix the schema and try again 
    up to 5 times. If it still fails, it will print the error message."""
    st.text(appdescription)
    user_input = get_user_input()
    run_llm(user_input, 5)
    download_schema()



init_app()
        
text = """
Example input:
```
MySinteringSchema:
  temperature: 394.5K
  process_finished: True
  user: Sebastian
```
"""
st.markdown(text)
#st.write("Example input:\n\nMySinteringSchema:\n  temperature: 394.5K\n  process_finished: True\n  user: Sebastian")