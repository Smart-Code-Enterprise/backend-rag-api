import json
import textwrap

def make_prompt(query, relevant_passage):
  escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
  prompt = textwrap.dedent("""QUESTION: '{query}'
                            f'Infomation': '{relevant_passage}'                          
                           Please generate a comprehensive answer based on the information provided.
                           You are act as Architectural engineer expert and your work is answer the question of junior engineer in the book and give answer with references. let's work this out in a step by step way to be sure we have the right answer, if dont know, please response dont know; always start the answer by 'according to ontario building code'
                           return full content of clause with number, such as:
                           question: What are the regulations for holes that may be drilled into roof truss members?
                           answer: ""9.23.5.5 Roof Trusses
(1)Roof truss members shall not be notched, drilled or otherwise weakened unless such notching or drilling is allowed for in the design of the truss.
9.23.5.1 Notching and Drilling
(1) Holes drilled in roof, floor or ceiling framing members shall be not larger than one-quarter the depth of the member and shall be located not less than 50 mm from the edges, unless the depth of the member is increased by the size of the hole."                           
                           
  PASSAGE: '{relevant_passage}'

    ANSWER:
  """).format(query=query, relevant_passage=escaped)

  return prompt

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)