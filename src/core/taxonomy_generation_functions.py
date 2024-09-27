import re
import logging

from src.prompts.prompt_templates import *
from src.core.helper_functions import update_token_usage

# Function to check if a taxonomy for the given root concept exists in the model
def check_accepted_taxonomy(root_concept:str, model_verify, context = "", max_tokens = 5, log = None) -> bool:
    if not log:
        log = logging.getLogger("check_accepted_taxonomy")
        logging.basicConfig(level=logging.INFO)
    log.info("check_accepted_taxonomy() function called!")
    log.info(f'Root concept: {root_concept}')
    log.info(f"Max tokens set to: {max_tokens}")

    # Prepare the prompt for the LLM based on the root concept and context
    prompt = chat_template_accepted_taxonomy_existance_check.format_messages(root_concept = root_concept, context = context)
    log.info(f"Accepted taxonomy check prompt:\n\n-------------------------------\n{prompt}\n\nInvoking LLM...")

    try:
        # Invoke the model to check for the existence of the accepted taxonomy
        response = model_verify.invoke(prompt, max_tokens=max_tokens)
        log.info(f"Accepted taxonomy check successful! Response: \n\n{response}\n\n")
        token_usage = response.response_metadata['token_usage']
        # Check if the response contains 'yes', indicating the existence of the taxonomy
        if len(re.findall('yes', response.content.lower().replace(" ", ''))) > 0:
            return True, token_usage
        else:
            log.info(f"Accepted taxonomy check successful! But taxonomy not found, response is: \n\n{response.content.lower().replace(' ','')}\n\n")
            return False, token_usage 
    except Exception as e:
        log.info(f"Accepted taxonomy check failed: {e}")
        token_usage = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
        return False, token_usage
        
# Function to check if a super-taxonomy (a higher-level taxonomy) exists for a given concept
def check_super_taxonomy(concept: str, model_verify, max_tokens = 5, log = None) -> bool:
    if not log:
        log = logging.getLogger("check_super_taxonomy")
        logging.basicConfig(level=logging.INFO)
    log.info("check_super_taxonomy() function called!")
    log.info(f'Concept: {concept}')
    log.info(f"Max tokens set to: {max_tokens}")

    # Prepare the prompt for the LLM based on the concept
    prompt = chat_template_super_taxonomy_existance_check.format_messages(concept=concept)
    log.info(f"Super taxonomy check prompt:\n\n-------------------------------\n{prompt}\n\nInvoking LLM...")

    try:
        # Invoke the model to check for the existence of a super-taxonomy
        response = model_verify.invoke(prompt, max_tokens=max_tokens)
        log.info(f"Super taxonomy check successful! Response: \n\n{response}\n\n")
        token_usage = response.response_metadata['token_usage']
        # Check if the response contains 'yes', indicating the existence of the super-taxonomy
        if len(re.findall('yes', response.content.lower().replace(" ", ''))) > 0:
            return True, token_usage
        else:
            log.info(f"Super taxonomy check successful! But super-taxonomy not found, response is: \n\n{response.content.lower().replace(' ','')}\n\n")
            return False, token_usage
    except Exception as e:
        log.info(f"Super taxonomy check failed: {e}")
        token_usage = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
        return False, token_usage
        
# Function to find the root of a super-taxonomy for a given concept
def find_super_taxonomy_root(concept: str, model_generate_new, max_tokens = 10, log = None) -> str:
    if not log:
        log = logging.getLogger("find_super_taxonomy_root")
        logging.basicConfig(level=logging.INFO)
    log.info("find_super_taxonomy_root() function called!")
    log.info(f'Concept: {concept}')
    log.info(f"Max tokens set to: {max_tokens}")

    # Prepare the prompt to find the super-taxonomy root for the given concept
    prompt = chat_template_super_taxonomy_find.format_messages(concept=concept)
    log.info(f"Super taxonomy root find prompt:\n\n-------------------------------\n{prompt}\n\nInvoking LLM...")

    try:
        # Invoke the model to find the root of the super-taxonomy
        response = model_generate_new.invoke(prompt, max_tokens=max_tokens)
        log.info(f"Super taxonomy root find successful! Response: \n\n{response}\n\n")
        token_usage = response.response_metadata['token_usage']
        found_root = response.content
    except Exception as e:
        log.info(f"Super taxonomy root find failed: {e}")
        token_usage = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
        found_root = "None"
    return found_root, token_usage
        
# Function to find taxonomical criteria for a given root concept
def find_taxonomical_criteria(root_concept: str, model_generate_new, context = "", max_tokens = 50, log = None) -> str:
    if not log:
        log = logging.getLogger("find_taxonomical_criteria")
        logging.basicConfig(level=logging.INFO)
    log.info("find_taxonomical_criteria() function called!")
    log.info(f'Root concept: {root_concept}')
    log.info(f"Max tokens set to: {max_tokens}")

    # Prepare the prompt to find taxonomical criteria based on the root concept and context
    prompt = chat_template_find_taxonomical_criteria.format_messages(root_concept=root_concept, context=context)
    log.info(f"Find taxonomical criteria prompt:\n\n-------------------------------\n{prompt}\n\nInvoking LLM...")

    try:
        # Invoke the model to find taxonomical criteria
        response = model_generate_new.invoke(prompt, max_tokens=max_tokens)
        log.info(f"Taxonomical criteria found successfully! Response: \n\n{response}\n\n")
        token_usage = response.response_metadata['token_usage']
        criteria = response.content
    except Exception as e:
        log.info(f"Taxonomical criteria find failed: {e}")
        token_usage = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
        criteria = "None"
    return criteria, token_usage
        
# Function to find taxonomical ranks for a given root concept
def find_taxonomical_ranks(root_concept: str, model_generate_new, context = "", max_tokens = 50, log = None) -> list:
    if not log:
        log = logging.getLogger("find_taxonomical_ranks")
        logging.basicConfig(level=logging.INFO)
    log.info("find_taxonomical_ranks() function called!")
    log.info(f'Root concept: {root_concept}')
    log.info(f'Context: {context}')
    log.info(f"Max tokens set to: {max_tokens}")

    # Prepare the prompt to find taxonomical ranks based on the root concept and context
    prompt = chat_template_find_taxonomical_ranks.format_messages(root_concept=root_concept, criteria=context)
    log.info(f"Find taxonomical ranks prompt:\n\n-------------------------------\n{prompt}\n\nInvoking LLM...")

    try:
        # Invoke the model to find taxonomical ranks
        response = model_generate_new.invoke(prompt, max_tokens=max_tokens)
        ranks_lists = response.content.replace('\n', ' ').replace('; ',';').split(';')
        ranks = [v.strip() for v in ranks_lists]
        ranks_lists = [v.replace(', ',',').split(',') for v in ranks]
        #ranks_list = [v.strip() for v in response.content.replace('\n', ' ').replace('/', ',').replace(';',',').replace('. ',', ').replace(', ', ',').replace(',,',',').replace('  ', ' ').replace("'","").split(",")]
        #ranks_list = [el for el in ranks_list  if len(el) > 3]
        log.info(f"Taxonomical ranks found successfully! Response: \n{response}\n\nTaxonomical ranks lists: {ranks_lists}")
        token_usage = response.response_metadata['token_usage']
    except Exception as e:
        log.info(f"Taxonomical ranks generation failed: {e}")
        ranks_list = ["None"]
        ranks_lists = [["None"]]
        token_usage = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
    return ranks_lists, token_usage
    #return ranks_list, token_usage

# Function to get descriptions for a given concept
def get_concept_descriptions_and_definitions(root_concept: str, model_generate_new, amount = 5, max_length = 50, max_tokens = 300, log = None) -> str:
    if not log:
        log = logging.getLogger("get_concept_descriptions_and_definitions")
        logging.basicConfig(level=logging.INFO)
    log.info("get_concept_descriptions_and_definitions() function called!")
    log.info(f'Max tokens set to: {max_tokens}. \nTarget concept: {root_concept}.\n')
    token_usage_total = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
    # generate definitions
    prompt_generate_definitions = chat_template_definitions.format_messages(root_concept=root_concept, definitions_amount=amount, definition_length = max_length)
    # generate descriptions
    prompt_generate_descriptions = chat_template_descriptions.format_messages(root_concept=root_concept, descriptions_amount=amount, description_length = max_length)
    try:
        # Generate expert and linguist descriptions using the model
        response = model_generate_new.invoke(prompt_generate_definitions, max_tokens=max_tokens)
        token_usage_total = update_token_usage(token_usage_total, response.response_metadata['token_usage'])
        descriptions = [el.strip() for el in response.content.split(";") if len(el.strip()) > 5]
        log.info(f"Concept descriptions generation successful! Response: \n\n{response}\n\n")
        response = model_generate_new.invoke(prompt_generate_descriptions, max_tokens=max_tokens)
        token_usage_total = update_token_usage(token_usage_total, response.response_metadata['token_usage'])
        definitions = [el.strip() for el in response.content.split(";") if len(el.strip()) > 5]
        log.info(f"Concept definitions generation successful! Response: \n\n{response}\n\n")
    except Exception as e:
        log.info(f"Concept definitions and descriptions generation failed: {e}") 
        descriptions = ["The description can not be generated!"]
        definitions =  ["The definition can not be generated!"]
    return descriptions, definitions, token_usage_total

# Function to generate a defined-length definition for a given concept
def get_concept_definition(concept: str, root_concept: str, taxonomical_rank: str, taxonomical_context: str, model_generate_new, definition_max_words = 10, max_tokens = 100, log = None) -> str:
    if not log:
        log = logging.getLogger("get_concept_definition")
        logging.basicConfig(level=logging.INFO)
    log.info("get_concept_definition() function called!")
    log.info(f'Definition max words: {definition_max_words}, Max tokens set to: {max_tokens}. \nTarget concept: {concept}.\nRoot concept: {root_concept}')

    # Prepare the prompt to generate a concise definition for the concept
    prompt = chat_template_define.format_messages(root_concept=root_concept, concept = concept, taxonomical_rank=taxonomical_rank, taxonomical_context=taxonomical_context, definition_length = definition_max_words)
    log.info(f"Definition generation prompt:\n\n-------------------------------\n{prompt}\n\nInvoking LLM...")

    try:
        # Generate the definition using the model
        response = model_generate_new.invoke(prompt, max_tokens=max_tokens)
        log.info(f"Concept definition generation successful! Response: \n\n{response}\n\n")
        token_usage = response.response_metadata['token_usage']
        return response.content, token_usage
    except Exception as e:
        log.info(f"Concept definition generation failed: {e}")
        token_usage = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
        return "The definition cannot be generated!", token_usage
  
# Function to create a list of subconcepts for a given concept
def create_subconcepts_list(concept: str, root_concept: str, taxonomical_rank: str, taxonomical_context: str, concept_definition: str, model_generate_new, max_tokens = 80, max_tokens_context = 100, max_words_context = 40, subconcepts_amount = 10, log = None) -> list:
    if not log:
        log = logging.getLogger("create_subconcepts_list")
        logging.basicConfig(level=logging.INFO)
    log.info(f'''create_subconcepts_list() \nTarget concept: {concept}\nRoot concept: {root_concept}..''')
    log.info(f"Selected taxonomical rank: {taxonomical_rank}\n({taxonomical_context})\nDefinition max words: {max_words_context}")
    
    # Prepare the context and prompt to generate subconcepts
    context_string = " " + concept_definition
    prompt = chat_template_list_subconcepts.format_messages(root_concept=root_concept, concept=concept, context_string=context_string, taxonomical_rank=taxonomical_rank, taxonomical_context=taxonomical_context, subconcepts_amount=subconcepts_amount)
    log.info(f"Subconcept listing generation prompt:\n\n-------------------------------\n{prompt}\n\nInvoking LLM...")

    try:
        # Generate the list of subconcepts using the model
        response = model_generate_new.invoke(prompt, max_tokens=max_tokens)
        subcat_list = response.content.replace(', ', ',').split(",")
        log.info(f"Subconcept listing generation successful! Response: \n{response}\n\nSubconcepts list: {subcat_list}")
        token_usage = response.response_metadata['token_usage']
    except Exception as e:
        log.info(f"Subconcept listing generation failed: {e}")
        subcat_list = ["None"]
        token_usage = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
    return subcat_list, token_usage

# Function to create a list of redundant subconcepts that can be discarded
def create_redundant_subconcepts_list(candidate_list: list, root_concept: str, taxonomical_rank: str, taxonomical_context: str, model_re_generate, max_tokens = 80, log = None) -> list:
    if not log:
        log = logging.getLogger("create_redundant_subconcepts_list")
        logging.basicConfig(level=logging.INFO)
    log.info(f'''create_redundant_subconcepts_list() \nRoot concept: {root_concept}..''')
    log.info(f"Selected taxonomical rank: {taxonomical_rank}\nTaxonomical context: {taxonomical_context}")

    # Prepare the prompt to identify and discard redundant subconcepts
    prompt = chat_template_discard_subconcepts.format_messages(root_concept=root_concept, taxonomical_rank=taxonomical_rank, taxonomical_context=taxonomical_context, candidate_list=candidate_list)
    log.info(f"Redundant subconcepts listing filter prompt:\n\n-------------------------------\n{prompt}\n\nInvoking LLM...")

    try:
        # Generate the list of redundant subconcepts using the model
        response = model_re_generate.invoke(prompt, max_tokens=max_tokens)
        subcat_list = response.content.replace(', ', ',').split(",")
        log.info(f"Redundant subconcept listing generation successful! Response: \n{response}\n\nRedundant subconcepts list: {subcat_list}")
        token_usage = response.response_metadata['token_usage']
    except Exception as e:
        log.info(f"Redundant subconcept listing generation failed: {e}")
        subcat_list = ["None"]
        token_usage = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
    return subcat_list, token_usage

# Function to create a list of redundant criteria lists
def create_redundant_criteria_list(candidate_lists: list, root_concept: str, model_re_generate, max_tokens = 20, log = None) -> list:
    if not log:
        log = logging.getLogger("create_redundant_criteria_list")
        logging.basicConfig(level=logging.INFO)
    log.info(f'''create_redundant_criteria_list() \nRoot concept: {root_concept}..''')
    context = ''
    for i,v in enumerate(candidate_lists):
        context+=str(i)+'. '+str(v)+'\n'
    # Prepare the prompt to identify and discard redundant criteria lists
    prompt = chat_template_discard_criteria.format_messages(root_concept=root_concept, candidate_lists=context)
    log.info(f"Redundant criteria listing filter prompt:\n\n-------------------------------\n{prompt}\n\nInvoking LLM...")

    try:
        # Generate the list of redundant criteria using the model
        response = model_re_generate.invoke(prompt, max_tokens=max_tokens)
        subcat_list = response.content.replace(', ', ',').split(",")
        log.info(f"Redundant criteria generation successful! Response: \n{response}\n\nRedundant criteria list: {subcat_list}")
        token_usage = response.response_metadata['token_usage']
    except Exception as e:
        log.info(f"Redundant criteria generation failed: {e}")
        subcat_list = ["None"]
        token_usage = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
    return subcat_list, token_usage

# Function to optimize multiple ranks lists
def optimize_ranks_lists(candidate_lists: list, root_concept: str, model_generate_new, max_tokens = 50, log = None) -> list:
    if not log:
        log = logging.getLogger("optimize_ranks_lists")
        logging.basicConfig(level=logging.INFO)
    log.info(f'''optimize_ranks_lists() \nRoot concept: {root_concept}..''')

    # Prepare the input by concatenating candidate lists from different experts
    lists_string = "Candidate lists:\n"
    for i, candidate_list in enumerate(candidate_lists):
        lists_string += f"{i}. {', '.join(str(candidate_list))};\n"#f"Expert {i}'s candidate list: ####{candidate_list}####\n"
    
    # Prepare the prompt to optimize the ranks lists
    prompt = chat_template_optimize_ranks_lists.format_messages(root_concept=root_concept, candidate_lists=lists_string)
    log.info(f"Rank lists optimization prompt:\n\n-------------------------------\n{prompt}\n\nInvoking LLM...")

    try:
        # Optimize the ranks lists using the model
        response = model_generate_new.invoke(prompt, max_tokens=max_tokens)
        subcat_list = [el.strip() for el in response.content.split(";") if len(el) > 0]
        log.info(f"Optimizing ranks list successful! Response: \n{response}\n\nOptimized ranks lists: {subcat_list}")
        token_usage = response.response_metadata['token_usage']
    except Exception as e:
        log.info(f"Optimizing ranks list failed: {e}")
        subcat_list = ["None"]
        token_usage = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
    log.info("Optimizing finished")
    return subcat_list, token_usage

# Function to postprocess the subconcepts list
def postprocess_subconcepts(root_concept: str, taxonomical_rank: str, subconcept_candidates: list, model_generate_new, max_tokens = 60, log = None) -> list:
    if not log:
        log = logging.getLogger("postprocess_subconcepts")
        logging.basicConfig(level=logging.INFO)
    log.info("postprocess_subconcepts() function called!")
    log.info(f'Root concept: {root_concept}, Taxonomical rank: {taxonomical_rank}, Candidates: {subconcept_candidates}')
    log.info(f"Max tokens set to: {max_tokens}")

    # Prepare the prompt to postprocess the subconcepts list
    prompt = chat_template_postprocess_subconcepts.format_messages(root_concept = root_concept, taxonomical_rank = taxonomical_rank, subconcept_candidates = str(subconcept_candidates)[1:-1])
    log.info(f"Postprocess subconcepts prompt:\n\n-------------------------------\n{prompt}\n\nInvoking LLM...")
    try:
        # Postprocess the subconcepts list using the model
        response = model_generate_new.invoke(prompt, max_tokens=max_tokens)
        subcat_list = response.content.replace(', ',',').split(",")
        log.info(f"Postprocess subconcepts successful! Response:\n{response}\n\nPostprocessed subconcepts list: {subcat_list}")
        token_usage = response.response_metadata['token_usage']
    except Exception as e:
        log.info(f"Postprocess subconcepts failed: {e}")
        subcat_list = subconcept_candidates
        token_usage = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
    return subcat_list, token_usage
