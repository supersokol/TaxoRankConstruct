import os
import logging
import datetime
import pickle
import re

import openai
from langchain_openai import ChatOpenAI
import nltk
from nltk.stem import WordNetLemmatizer 
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL

def ensure_directory_exists(path):

    # Validation
    if not os.path.exists(path):
        try:
            # Direcrotry creation
            os.makedirs(path)
            print(f"Directory created: {path}")
        except OSError as error:
            print(f"Error creating directory: {error}")
    else:
        print(f"Directory already exists: {path}")

# Class for initializing a Large Language Model (LLM) 
class Model:
    def __init__(self, name:str, model_checkpoint:str, temperature = 1, top_p = 1, presence_penalty = 1, frequency_penalty = 0) -> None:
        self.model              = ChatOpenAI(
                model               = model_checkpoint, 
                temperature         = temperature, 
                top_p               = top_p, 
                presence_penalty    = presence_penalty, 
                frequency_penalty   = frequency_penalty
            )
        self.name               = name
        self.temperature        = temperature
        self.model_checkpoint   = model_checkpoint
        self.top_p              = top_p
        self.presence_penalty   = presence_penalty
        self.frequency_penalty  = frequency_penalty
        self.info               = f'''model name: {name}
model checkpoint: {model_checkpoint}
temperature: {temperature}
top p: {top_p}
presence penalty: {presence_penalty}
frequency penalty: {frequency_penalty}'''

# Class representing a concept within the taxonomy
class Concept:
    def __init__(self, concept_name: str, parent = None, taxonomical_rank = 'root', taxonomical_level = 0, taxonomical_ranks_list_number = 'root') -> None:
        self.name = concept_name
        self.descriptions = []
        self.definitions = []
        self.definition = ""
        self.children = []
        self.parent = parent
        self.taxonomical_rank = taxonomical_rank
        self.taxonomical_level = taxonomical_level
        self.taxonomical_ranks_list_number = taxonomical_ranks_list_number
    
    # Method to print detailed information about the concept
    def info(self, parent = None, i = 0) -> None:
        print('\n\n'+'-+'*i+f"Concept\nname: {self.name}")
        if self.definition:
            print(f"definition: {self.definition}")
        print(f"taxonomical rank:{self.taxonomical_rank}"+' '*i+f"\ntaxonomical level:{self.taxonomical_level}\ntaxonomical ranks list number = {self.taxonomical_ranks_list_number}")
        if self.definitions:
            print(f"has {len(self.definitions)} definitions: {self.definitions}")
        if self.descriptions:
            print(f"has {len(self.descriptions)} descriptions: {self.descriptions}")
        i += 1
        if self.parent:
            print('---'*i+f"is subconcept of: {self.parent.name}")
        if len(self.children) > 0:
            print('---'*i+f"has {len(self.children)} subconcepts:")
            for concept in self.children:
                concept.info(parent = self, i = i)
       
    # Method to get the semantic cotopy (hypernyms and hyponyms)
    def get_semantic_cotopy(self, lemmatized=True):
        hypernyms = []
        hyponyms = []
        
        # Helper function to recursively collect hypernyms
        def get_hypernyms(self, hypernyms):
            if self.parent:
                hypernyms.append(self.parent)
                get_hypernyms(self.parent, hypernyms)
        
        # Helper function to recursively collect hyponyms
        def get_hyponyms(self, hyponyms):
            if self.children:
                hyponyms += self.children
                for child in self.children:
                    get_hyponyms(child, hyponyms)
        
        get_hypernyms(self, hypernyms)
        get_hyponyms(self, hyponyms)
        
        if not lemmatized:
            return hypernyms, hyponyms
        else:
            hypernyms_list = [lemmatize_word(hypernym.name) for hypernym in hypernyms]
            hyponyms_list = [lemmatize_word(hyponym.name) for hyponym in hyponyms]
            return hypernyms_list + hyponyms_list

# Class representing the taxonomy structure    
class Taxonomy:
    
    def __init__(self, root_concept_name:str) -> None:
        self.created_at             = datetime.datetime.now()
        self.last_edit_time         = datetime.datetime.now()
        self.name                   = 'Taxonomy_'+str(self.created_at).replace(' ','_T').replace(':','-')[:22]
        self.save_path              = os.getcwd()+"\\data\\taxonomies\\"
        self.saved_to               = [self.save_path + self.name + '.pkl']
        self.token_usage            = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}

        self.root                   = Concept(root_concept_name)

        self.taxonomical_criteria   = []
        self.raw_criteria           = []
        self.taxonomical_ranks_list = []
        self.taxonomical_ranks      = []
        self.taxonomical_context    = []
        
        self.current_level          = []
        self.uninspected_concepts   = []
        self.unknown_concepts       = [[]]
        self.concepts               = [self.root]
        
        
        fp = self.save()
    
    # Method to print detailed information about the taxonomy
    def info(self) -> None:
        print(f"--------INFO:-------\n\n--------ROOT:-------\nroot concept of the current taxonomy is: \"{self.root.name}\"\n")
        print("---------CRITERIA:---")
        #print(f"taxonomical criteria of the current taxonomy are: \nAll criteria:\n{self.raw_criteria}\n\ncriteria clusters:\n")
        print(f"taxonomical criteria of the current taxonomy are: \nAll criteria:\n{self.taxonomical_criteria}\n\n")
        
        #for i,criteria in enumerate(self.taxonomical_criteria):
        #    print(f"Cluster {i+1}/{len(self.taxonomical_criteria)}. Criteria:\n{criteria}\n")
        print("\n\n---------RANKS:-----\n--------------------\n")
        print(f"there are {len(self.taxonomical_ranks)} taxonomical ranks lists in the current taxonomy:\n")
        for i,rank in enumerate(self.taxonomical_ranks):
            #print(f"{rank}")
            if i <= 1:
                k = 0
                
            else:
                k = i - 1
            #try:
            #    print(f" {i}. rank '{rank.replace(', ',',').split(',')[self.current_level[k]]}' in '{self.taxonomical_context[k]}'(taxonomical level is {self.current_level[i]})")
            #except Exception as e:
            #    print(f" {i}. rank '{rank.replace(', ',',').split(',')[self.current_level[i]]}' in '{self.taxonomical_context[i]}'(taxonomical level is {self.current_level[i]})")
            try:
                print(f" {i}. rank '{rank.replace(', ',',').split(',')[self.current_level[i]]}' in '{self.taxonomical_context[i]}'(taxonomical level is {self.current_level[i]})")
            except Exception as e:
                print(f" {i}. rank '{rank.replace(', ',',').split(',')[-1]}' in '{self.taxonomical_context[i]}'(taxonomical level is {self.current_level[i]})")
        print("\n\n---------CONCEPTS:---\n--------------------\n")
        print(f"total amount of concepts in the current taxonomy is {len(self.concepts)}")
        print(f"total amount of uninspected concepts in the current taxonomy is {len(flatten(self.uninspected_concepts))}")
        print(f"total amount of unknown concepts in the current taxonomy is {len(flatten(self.unknown_concepts))}")
        print("\n--CREATED/EDITED----")
        print(f"taxonomy creation time: {str(self.created_at)}\nlast_edit time: {str(self.last_edit_time)}")
        print("\n---TOKEN USAGE:-----")
        print(f"\n\ncurrent token usage total: \n{self.token_usage}\n")
        #print(f"the current taxonomical level is {self.current_level} level\ncorresponding rank is {self.taxonomical_ranks[self.current_level]}")
        print("\n------SAVED TO:-----")
        if len(self.saved_to)>1:
            print(f"taxonomy was saved to {len(self.saved_to)} diferent paths total: {self.saved_to}")
        print(f"f'taxonomy last saved at '{self.save_path+self.name}.pkl'\n")
        print(f"--------------------\n--------/INFO-------\n--------------------\n\n")

    def update_last_edit_time(self) -> None:
        self.last_edit_time              = datetime.datetime.now()

    # Method to save the taxonomy to a file
    def save(self, suffix = "") -> str:
        ensure_directory_exists(self.save_path)
        full_path = self.save_path + self.name + suffix + '.pkl'
        with open(full_path, 'wb') as file:
            pickle.dump(self, file)
        if not full_path in self.saved_to:
            self.saved_to.append(full_path) 
        return full_path

    # Method to export the taxonomy to an OWL file
    def export_to_owl(self, suffix =''):
        ensure_directory_exists(self.save_path)
        file_path = self.save_path + self.name + suffix + '.owl'
        g = Graph()

        EX = Namespace("urn:ontology/")  # Replace with your URI base
        g.bind("ex", EX)

        # Add root concept
        root_concept = URIRef(EX[self.root.name])
        g.add((root_concept, RDF.type, OWL.Class))
        g.add((root_concept, RDFS.label, Literal(self.root.name)))

        # Recursively add all subconcepts
        def add_concept_to_graph(concept):
            concept_uri = URIRef(EX[concept.name])
            g.add((concept_uri, RDF.type, OWL.Class))
            g.add((concept_uri, RDFS.label, Literal(concept.name)))

            for child in concept.children:
                child_uri = URIRef(EX[child.name])
                g.add((child_uri, RDF.type, OWL.Class))
                g.add((child_uri, RDFS.label, Literal(child.name)))
                g.add((child_uri, RDFS.subClassOf, concept_uri))
                add_concept_to_graph(child)

        # Start recursion from the root concept
        add_concept_to_graph(self.root)

        # Save the graph to an OWL file
        g.serialize(destination=file_path, format='xml')
        print(f"Taxonomy exported to {file_path}")

# Helper function for flattening nested lists
def flatten(xss):
    return [x for xs in xss for x in xs]

# Initialize the WordNet Lemmatizer
lemmatizer = WordNetLemmatizer()

# Helper function for lemmatizing words
def lemmatize_word(word: str):
    try:
        try:
            word_list = nltk.word_tokenize(word)
        except:
            nltk.download('punkt_tab')
            word_list = nltk.word_tokenize(word)
        lemmatized_output = ' '.join([lemmatizer.lemmatize(w.strip()) for w in word_list])#.lower()
    except Exception as e:
            lemmatized_output = word.strip()#.lower()
    return lemmatized_output

# Initialize logging and load API credentials
def start_session(api_key = None): 
    start_time = datetime.datetime.now()
    log = logging.getLogger("TaxoRankConstruct")
    logs_path = os.getcwd()+"\\logs\\"
    ensure_directory_exists(logs_path)
    log_name = 'TaxoRankConstruct_0.1__'+str(start_time).replace(' ','_').replace(':','-')[:21]+'.log'
    logging.basicConfig(filename=logs_path+log_name, level=logging.INFO)
    log.info("start_session()")
    # Set your OpenAI API key
    if not api_key:
        log.info("OPENAI API KEY NOT PROVIDED!!")
    else:
        os.environ["OPENAI_API_KEY"] = api_key
    openai.api_key = os.environ["OPENAI_API_KEY"]
    return log

# Initialize models for the taxonomy construction
def init_models(log = None):
    if not log:
        log = logging.getLogger("init_models()")
        logging.basicConfig(level=logging.INFO)
    log.info(f"init_models()..")
    
    # Verification model
    llm_verify              = Model('verify',       'gpt-4o-mini',  
                                    temperature = 0.9,    top_p = 0.90,   presence_penalty = 1.00,   frequency_penalty = 0.00) 
    log.info(f"{llm_verify.info}\nmodel init successfully..")
    model_verify            = llm_verify.model
    
    # Re-Generation model
    llm_re_generate         = Model('re-generate',  'gpt-4o-mini',
                                    temperature = 1.3,    top_p = 0.90,   presence_penalty = 0.50,   frequency_penalty = 1.00)
    log.info(f"{llm_re_generate.info}\nmodel init successfully..")
    model_re_generate       = llm_re_generate.model
    
    # New concept generation model
    llm_generate_new        = Model('generate new',  'gpt-4o',
                                    temperature = 1.0,    top_p = 0.98,   presence_penalty = 1.00,   frequency_penalty = 1.20)
    log.info(f"{llm_generate_new.info}\nmodel init successfully..")
    model_generate_new      = llm_generate_new.model
    log.info(f"model_generate_new, model_re_generate, model_verify models initialized")
    return model_generate_new, model_re_generate, model_verify

# Function to load a saved taxonomy from a file
def load_taxonomy(file_path:str) -> Taxonomy:
    # Deserialize the object from the binary file
    with open(file_path, 'rb') as file:
        loaded_taxonomy = pickle.load(file)
    return loaded_taxonomy

# Function for the token usage update
def update_token_usage(token_usage, token_usage_delta):
    res = {}
    for key in token_usage.keys():#['completion_tokens', 'prompt_tokens','total_tokens']:
        res[key] = token_usage[key] + token_usage_delta[key]
    return res

#EXAMPLE USAGE:
#______________________
#from src.core.helper_functions import start_session, init_models
#api_key = "yours_api_key"
#log = start_session(api_key)
#model_generate_new, model_re_generate, model_verify = init_models(log)

#from src.core.helper_functions import Concept, Taxonomy, load_taxonomy
#target_concept = "lumber wood"
#test_concept = Concept(target_concept, parent = None, taxonomical_rank = 'root', taxonomical_level = 0, taxonomical_ranks_list_number = 'root')
#test_concept.info()
#taxonomy_new = Taxonomy(target_concept)
#taxonomy_new.info()
#taxonomy_new.root.info()

#taxonomy_path = taxonomy_new.saved_to[0]
#taxonomy_loaded = load_taxonomy(taxonomy_path)
#taxonomy_loaded.info()
#taxonomy_loaded.root.info()
#______________________

