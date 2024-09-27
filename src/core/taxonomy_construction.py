import logging

from src.core.helper_functions import Taxonomy, Concept, update_token_usage, flatten
from src.core.taxonomy_generation_functions import *

def construct_taxonomy(root_concept, model_generate_new, model_re_generate, model_verify, definition_amount = 5, definition_max_words = 50, log = None, check_existance = False):
    if not log:
        log = logging.getLogger("create_taxonomy")
        logging.basicConfig(level=logging.INFO)
    log.info(f"create_taxonomy() function called!\nroot_concept candidate is {root_concept}\nstep 1 - check if {root_concept} is accepted ROOT concept of some taxonomy...")
    token_usage_total = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
    try:
        if check_existance:
            accepted_root, token_usage = check_accepted_taxonomy(root_concept, model_verify, log = log)
            token_usage_total = update_token_usage(token_usage_total, token_usage)
        else:
            accepted_root = True
        if accepted_root: 
                log.info(f"{root_concept} is accepted ROOT concept for taxonomy construction.")
                taxonomy = Taxonomy(root_concept)
                taxonomy.root.descriptions, taxonomy.root.definitions, token_usage = get_concept_descriptions_and_definitions(root_concept, model_generate_new, amount = definition_amount, max_length = definition_max_words, log = log)
                token_usage_total = update_token_usage(token_usage_total, token_usage)
        if not accepted_root:
            log.info(f"{root_concept} is not accepted root concept for taxonomy construction!")
            log.info(f"step 1.1 - check if {root_concept} is accepted concept INSIDE of some taxonomy...")
            for i in range(0,5):
                accepted_part, token_usage = check_super_taxonomy(root_concept,model_verify,log=log)
                token_usage_total = update_token_usage(token_usage_total, token_usage)
                if accepted_part:
                    log.info(f"{root_concept} is accepted concept INSIDE of some taxonomy. {i} iterations performed.")
                    log.info(f"step 1.2 - find accepted ROOT concept for such taxonomy...")
                    for i in range(0,5):
                        new_root_concept, token_usage = find_super_taxonomy_root(root_concept,model_generate_new,log=log)
                        token_usage_total = update_token_usage(token_usage_total, token_usage)
                        log.info(f"The accepted ROOT concept of the taxonomy is {new_root_concept}.. {i} \niterations performed.")
                        taxonomy = Taxonomy(new_root_concept)
                        taxonomy.root.descriptions, taxonomy.root.definitions, token_usage = get_concept_descriptions_and_definitions(root_concept, model_generate_new, amount = definition_amount, max_length = definition_max_words, log = log)
                        token_usage_total = update_token_usage(token_usage_total, token_usage)
                        break
                    break
            if not accepted_part:
                log.info(f"{root_concept} concept is not a part of any accepted taxonomy..")
                taxonomy = Taxonomy(None)
                taxonomy.uninspected_concepts.remove(taxonomy.root)
                log.info(f'finished - empty taxonomy created...')
                return taxonomy
        log.info(f'step 1 finished - taxonomy with the root concept {taxonomy.root.name} created, {len(taxonomy.root.descriptions)} descriptions and {len(taxonomy.root.definitions)} definitions generated for the concept...\nstep 2 - for created taxonomy we will try to find taxonomical criteria...')
        for definition in taxonomy.root.descriptions + taxonomy.root.definitions:
            criteria, token_usage = find_taxonomical_criteria(taxonomy.root.name,model_generate_new, context = definition, log = log)
            token_usage_total = update_token_usage(token_usage_total, token_usage)
            taxonomy.taxonomical_criteria.append(criteria)
        log.info(f'step 2 finished - taxonomical criteria are: {taxonomy.taxonomical_criteria}')
        filtered_criteria, token_usage = create_redundant_criteria_list(taxonomy.taxonomical_criteria, taxonomy.root.name, model_re_generate, log = log)
        token_usage_total = update_token_usage(token_usage_total, token_usage)
        try:
            try:
                taxonomical_criteria = [criteria for criteria in taxonomy.taxonomical_criteria if ( criteria.lower() not in [str(v).lower() for v in filtered_criteria] and len(criteria)>3 )]
                taxonomy.taxonomical_criteria = taxonomical_criteria
            except Exception as e:
                    log.info(f"failed: {e}")
            for i,redundant_criteria in enumerate(filtered_criteria):
                try:
                    taxonomy.taxonomical_criteria.pop(int(redundant_criteria)-i)
                except Exception as e:
                    log.info(f"removing criteria failed: {e}")
            log.info(f'step 2.5 finished - filtered taxonomical criteria are: {taxonomy.taxonomical_criteria}')        
        except Exception as e:
                log.info(f"filtering failed: {e}")
        
        log.info(f'step 3 - for created taxonomy we will try to use our taxonomical criteria to find out taxonomical ranks...')
        for i, criteria in enumerate(taxonomy.taxonomical_criteria):
            log.info(f'criteria {i}/{len(taxonomy.taxonomical_criteria)}: {criteria}')
            ranks, token_usage = find_taxonomical_ranks(taxonomy.root.name, model_generate_new, context = criteria, log = log)
            token_usage_total = update_token_usage(token_usage_total, token_usage)
            log.info(f'taxonomical ranks are: {ranks}')
            taxonomy.taxonomical_ranks.append(ranks)
        log.info(f'step 3 finished - taxonomical ranks are: {taxonomy.taxonomical_ranks}')
        taxonomy.taxonomical_ranks, token_usage = optimize_ranks_lists(taxonomy.taxonomical_ranks, taxonomy.root.name, model_generate_new, log = log)
        token_usage_total = update_token_usage(token_usage_total, token_usage)
        taxonomy.taxonomical_ranks = [el.replace('\n','') for el in taxonomy.taxonomical_ranks if len(el.replace('\n',''))>3]
        log.info(f'step 3.1 finished - optimized taxonomical ranks are: {taxonomy.taxonomical_ranks}')
        for ranks in taxonomy.taxonomical_ranks:
            try:
                ranks = ranks.replace(', ',',').split(",")
                taxonomy.current_level.append(0)
                taxonomical_context = ""
                for rank in ranks:
                    taxonomical_context += rank+" > "
                taxonomy.taxonomical_context.append(taxonomical_context[:-3])
                taxonomy.uninspected_concepts.append([taxonomy.root])
                taxonomy.unknown_concepts.append([])
                log.info(f'taxonomical ranks: {taxonomy.taxonomical_context[-1]}')
            except Exception as e:
                log.info(f"fail: {e}")
                print(f"fail: {e}")
    except Exception as e:
        log.info(f"taxonomy creation failed: {e}")
        taxonomy = Taxonomy(None)
        taxonomy.uninspected_concepts = [[]]
        log.info(f'finished - empty taxonomy created...')
    log.info(f'total_token_usage: \n\n{token_usage_total}\n\n')
    taxonomy.token_usage = update_token_usage(taxonomy.token_usage, token_usage_total)
    taxonomy_path = taxonomy.save()
    log.info(f'taxonomy saved as {taxonomy_path}')
    return taxonomy

def iterate_level(taxonomy, rank_number, model_generate_new, model_re_generate, model_verify, max_iter = 100, log = None, iteration_amm = 5, max_words_context= 40, max_subconcept_lenght = 80):
    if not log:
        log = logging.getLogger("iterate_level")
        logging.basicConfig(level=logging.INFO)
    log.info(f'iterate_level() \ntarget current level is {taxonomy.current_level[rank_number] + 1}')
    token_usage_total = {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
    try:
        log.info(f'taxonomical ranks are {taxonomy.taxonomical_ranks[rank_number]}')
        if taxonomy.current_level[rank_number]>len(taxonomy.taxonomical_ranks[rank_number].split(','))+1:
            log.info('out of ranks.. finishing')
            taxonomy.uninspected_concepts[rank_number] = []
            return taxonomy
        new_concepts = []
        current_rank = taxonomy.taxonomical_ranks[rank_number].split(',')[taxonomy.current_level[rank_number]]
        log.info(f'target taxonomical rank is {current_rank}')
        taxonomy.current_level[rank_number] += 1
        inspected_subconcepts = []
        print(f'{taxonomy.uninspected_concepts[rank_number]}')
        for j, concept in enumerate(taxonomy.uninspected_concepts[rank_number]):
            log.info(f'processing concept: {concept.name}')
            log.info(f'{j}/{len(taxonomy.uninspected_concepts[rank_number])-1} uninspected')
            log.info(f'concept\'s taxonomical rank is: {concept.taxonomical_rank}')
            log.info(f"ranks amount in current ranks list: {len(taxonomy.taxonomical_ranks[rank_number].split(','))}")
            log.info(f'concept\'s taxonomical level is: {concept.taxonomical_level}')
            if concept.taxonomical_level>=len(taxonomy.taxonomical_ranks[rank_number].split(',')):
                log.info(f'skipping concept {concept.name}')
                pass
            else:
                target_level = concept.taxonomical_level + 1
                current_rank = taxonomy.taxonomical_ranks[rank_number].split(',')[target_level - 1]
            log.info(f'so sub-concept\'s target taxonomical rank must be: {current_rank}\ngenerating target subconcept definition... max lenght is {max_words_context}')
            if not concept.definition:
                concept.definition, token_usage = get_concept_definition(concept.name, taxonomy.root.name, concept.taxonomical_rank, taxonomy.taxonomical_context[rank_number], model_generate_new, definition_max_words = max_words_context, log = log)
                token_usage_total = update_token_usage(token_usage_total, token_usage)
            log.info(f'sub-concept\'s definition generated: {concept.definition}')
            
            subconcepts_suitable = False
            i=0
            while not subconcepts_suitable:
                log.info(f'sub-concepts generation\n iteration: {i}/{iteration_amm}\n')
                log.info(f'total_token_usage: \n\n{token_usage_total}\n\n')
                i+=1
                subconcepts, token_usage = create_subconcepts_list(concept.name, taxonomy.root.name, current_rank, taxonomy.taxonomical_context[rank_number], concept.definition, model_generate_new, max_tokens=2800, max_tokens_context=600, max_words_context=50, log=log)
                token_usage_total = update_token_usage(token_usage_total, token_usage)
                subconcepts = [subconcept.replace("\n"," ") for subconcept in set(subconcepts) if len(subconcept) <= max_subconcept_lenght]  
                log.info(f"sub-concept candidates are {subconcepts}")
                subconcepts, token_usage = postprocess_subconcepts(taxonomy.root.name, current_rank, subconcepts, model_generate_new, log=log)
                token_usage_total = update_token_usage(token_usage_total, token_usage)
                log.info(f"sub-concept candidates postprocessed: {subconcepts}")
                validation_prompt = chat_template_check_subconcepts.format_messages(response = subconcepts, root_concept = taxonomy.root.name, taxonomical_rank = current_rank)
                log.info(f"sub-concept candidates validation prompt: {validation_prompt}")
                check_result = model_verify.invoke(validation_prompt, max_tokens = 20)
                log.info(f"sub-concept candidates validation result: {check_result}")
                token_usage = check_result.response_metadata['token_usage']
                token_usage_total = update_token_usage(token_usage_total, token_usage)
                if i>iteration_amm:
                    subconcepts_suitable = True
                    subconcepts = []
                    log.info(f"sub-concepts list generation failed after {iteration_amm} iterations...\nconcept {concept.name} added to unknown concepts list")
                    concept.children = []
                    taxonomy.unknown_concepts[rank_number].append(concept)
                elif check_result.content.replace(' ','') == "+":
                    subconcepts_suitable = True
                    log.info(f"sub-concepts list generated: {subconcepts}")
                    redundant_subconcepts, token_usage = create_redundant_subconcepts_list(subconcepts, taxonomy.root.name, current_rank, taxonomy.taxonomical_context[rank_number], model_re_generate, max_tokens = 400, log=log)
                    token_usage_total = update_token_usage(token_usage_total, token_usage)
                    log.info(f"redundant sub-concepts list generated: {redundant_subconcepts}")
                    if len(redundant_subconcepts)>len(subconcepts)*4/5:
                        log.info(f"more than 80 percent of sub-concepts are redundant, trying again.")
                        subconcepts_suitable = False
                    else:
                        redundant_subconcepts = [subconcept.lower() for subconcept in redundant_subconcepts]
                        subconcepts = [subconcept for subconcept in subconcepts if len(subconcept)<120]
                        subconcepts = [subconcept for subconcept in subconcepts if subconcept.lower() not in redundant_subconcepts]
                        log.info(f"sub-concepts list filtered: {subconcepts}")
            known_subconcepts = [c.name.lower() for c in taxonomy.concepts]
            nc = [Concept(subconcept, parent=concept, taxonomical_rank=current_rank, taxonomical_level=target_level, taxonomical_ranks_list_number=rank_number) for subconcept in subconcepts if subconcept.lower() not in known_subconcepts]
            concept.children += nc
            new_concepts += nc
            inspected_subconcepts.append(concept)
            taxonomy.concepts += nc
            taxonomy.token_usage = update_token_usage(taxonomy.token_usage, token_usage_total)
            taxonomy_path = taxonomy.save()
            log.info(f'taxonomy saved as {taxonomy_path}')
            if j>= max_iter:
                taxonomy.uninspected_concepts[rank_number] = new_concepts + [c for c in taxonomy.uninspected_concepts[rank_number] if c not in inspected_subconcepts]
                log.info(f'{j} uninspected concepts proceed. {len(taxonomy.uninspected_concepts[rank_number])} new concepts found, breaking generation....')
                break
        log.info(f'all currently unexplored concepts processed! {len(taxonomy.uninspected_concepts[rank_number])} new concepts found..')
        taxonomy.uninspected_concepts[rank_number] = new_concepts
        u_l = [c.name for c in flatten(taxonomy.uninspected_concepts)]
        log.info(f"finish!\nuninspected concepts (total) after the iteration: {u_l}")
    except Exception as e:
        log.info(f"iterate_level() failed: {e}")
    log.info('iterate_level proceed..')
    log.info(f'total_token_usage: \n\n{token_usage_total}\n\n')
    taxonomy.token_usage = update_token_usage(taxonomy.token_usage, token_usage_total)
    taxonomy_path = taxonomy.save()
    log.info(f'taxonomy saved as {taxonomy_path}')
    return taxonomy

#EXAMPLE USAGE:
#______________________
#
#
#from src.core.taxonomy_construction import create_taxonomy, iterate_level
#root_concept = "lumber wood"
#print(f"target concept is: {root_concept}\ncreating the taxonomy.....")
#tax_t = create_taxonomy(root_concept, model_generate_new, model_re_generate, model_verify)
#tax_t = iterate_level(tax_t, 0, model_generate_new, model_re_generate, model_verify)
#print(f"chosen taxonomical ranks list: {tax_t.taxonomical_ranks[0]}")
#u_l = [c.name for c in flatten(tax_t.uninspected_concepts)]
#print(f"finish!\nuninspected concepts after the iteration: {u_l}")
#tax_t.info()
#tax_t.root.info()

#from src.core.helper_functions import load_taxonomy
#loaded_tax = load_taxonomy(tax_t.saved_to[0])
#taxonomy_loaded.info()
#taxonomy_loaded.root.info()
#______________________