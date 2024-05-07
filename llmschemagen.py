from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import sys
from nomad.client import parse, normalize_all
import yaml
import ast
import streamlit as st
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


prompt = ChatPromptTemplate.from_template(cheatsheet + "{userpromp}")
output_parser = StrOutputParser()
chain = prompt | llm | output_parser



def invokechain(userinput):
    #userinput = input("Please enter your input: ")

    return chain.invoke({"userpromp": userinput }) 
# Title of the app
st.title('Invoke Chain App')

# Text input field
# user_input = st.text_input("Please enter your input:")
user_input = st.text_area("Enter your text here:")

# Button
if st.button('Invoke Chain'):
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
    counter=1
    error = None
    try:
        # Replace this with the actual parse command
        parse('output.schema.archive.yaml')
    except Exception as e:
        error = e
        st.write(f"An error occurred: {error}")
    
        for counter in range(5):
            #counter += 1
            st.write(counter)
            result = invokechain("You produced the following schema:" + result + "\n It returned this error: " + str(error) + "Please fix the schema and try again.")
            #result = yaml.safe_load(ast.literal_eval(result))
            with open('output2.schema.archive.yaml', 'w') as file:
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
                parse('output2.schema.archive.yaml')
                break
            except Exception as e:
                error = e
                st.write(f"An error occurred: {error}")
        # Display the result

    st.write("``` \n" + result)
    #else:
        


""" 
MySinteringSchema:
  temperature: 34.5°
  process_finished: True
  user: Sebastian"
              """