from langchain.prompts import ChatPromptTemplate

# ROOT CONCEPT DESCRIPTIONS (ONTOLOGICAL EXPERT)
#
# Name: chat_template_define_root_expert
# Parameters: description_amount, root_concept, description_length
# Description: Generates multiple distinct descriptions for the specified root concept, focusing on different aspects of the concept that are relevant for taxonomical classification. The descriptions are provided in a semicolon-separated format.
# Expected Result: Returns a semicolon-separated list of comprehensive and diverse descriptions for the given root concept.

chat_template_descriptions = ChatPromptTemplate.from_messages(
        [
            ("system", '''Role: You are an outstanding ontologist expert. Renowned worldwide for your unparalleled ontology expertise, you have a distinct passion for classifying various ambiguous concepts.
Context: Your mission is to deliver the top {descriptions_amount} most comprehensive and diverse explanations of the concepts referred to by the term "{root_concept}".
These descriptions should later serve as foundational concept descriptions for different taxonomical classifications. So each description must highlight different important sides of the concept.  
Instructions: The user requests multiple descriptions for a particular term. First, identify all the concepts defined by this term and choose exactly the {descriptions_amount} best distinctive concepts among them. Then generate descriptions for those concepts (one description for one concept). These descriptions should be the appropriate root concept definitions in taxonomy construction tasks.
Constraints: Skip all non-descriptions-itself stuff: explanations, tags, formatting, references, etc. You must always use a semicolon-separated format. All provided descriptions must be sufficient for the described concept's classification, and finding its sub-concepts.  Please sort the resulting definitions by their general frequency of use. Skip explanations and return descriptions in a semicolon-separated format like this: accepted description; another accepted description; another accepted description; etc.'''
),
            ("human", "Now provide exactly {descriptions_amount} different descriptions of the ontological concepts known by the name of \"{root_concept}\". Each description must contain at least {description_length} words. \n"),
            ("ai", "Descriptions: ")
        ]
    )

# ROOT CONCEPT DEFINITIONS (LINGUIST)
#
# Name: chat_template_define_root_linguist
# Parameters: definition_amount, root_concept, definition_length
# Description: Generates multiple distinct definitions for the specified root concept, focusing on delivering precise and enlightening definitions. The definitions are provided in a semicolon-separated format.
# Expected Result: Returns a semicolon-separated list of comprehensive and diverse definitions for the given root concept.

chat_template_definitions = ChatPromptTemplate.from_messages(
        [
            ("system", '''Role: You are an outstanding linguist. Renowned worldwide for your brilliant linguistic expertise and admirable erudition, you take particular delight in exploring the distinctions among definition variations of different ambiguous words. You can define every existing term in all possible ways.
Context: Your mission is to deliver the top {definitions_amount} most comprehensive and diverse explanations of the concepts referred to by the term "{root_concept}".
Each explanation must be precise and enlightening. Those explanations must deliver the best possible representation of the concepts denoted by the term. Those definitions of concepts must be peculiar, educative, and distinctive.
Instructions: The user asks you to provide several ({definitions_amount}) definitions for some specific term. At first, you must discover all the concepts defined by this term. Then choose exactly the {definitions_amount} best distinctive concepts among them. After this, you must generate a suitable definition for every chosen concept. The main purpose of those definitions is to serve as descriptions for the root concepts of different taxonomies. So definitions must be generally acceptable for the different taxonomical classifications root concepts. 
Constraints: Skip all non-descriptions-itself stuff: explanations, tags, formatting, references, etc. You must always use a semicolon-separated format. All provided definitions must be sufficient for understanding the most important features needed for the classification of the described concept's subconcepts. Please sort the results by their frequency of use. Skip explanations and return definitions in a semicolon-separated format like this: accepted definition; another accepted definition; another accepted definition; etc.'''
),
("human", "Now provide exactly {definitions_amount} different definitions of the ontological concepts defined by the term \"{root_concept}\". Each definition must contain at least {definition_length} words.  \n"),
            ("ai", "Definitions: ")
        ]
    )

# DEFINE TARGET CONCEPT
#
# Name: chat_template_define
# Parameters: root_concept, taxonomical_rank, taxonomical_context, definition_length, concept
# Description: Generates a definition for the specified concept within the context of a given taxonomical rank and hierarchy.
# Expected Result: Returns a single definition of the target concept, tailored to fit within the provided taxonomical context.

chat_template_define = ChatPromptTemplate.from_messages(
        [
            ("system", '''Role: You are the best ontology expert in the whole world with a particular interest in \"{root_concept}\" classification. 
Context: We are currently at the "{taxonomical_rank}" level in the hierarchy ({taxonomical_context}). The root concept of the taxonomy is {root_concept}. Use this information, to better understand the broader taxonomical structure and generate concept definitions more accurately and effectively.'''
),
            ("human", "Give a {definition_length} word length definition for the {taxonomical_rank} of the ontological concept \"{concept}\"  for our taxonomy. \n\n"),
            ("ai", "Definition: ")
        ]
    )

# CHECK EXISTENCE OF TAXONOMY WITH TARGET ROOT CONCEPT
#
# Name: chat_template_accepted_taxonomy_existance_check
# Parameters: root_concept, context
# Description: Checks if an accepted taxonomy exists with the specified root concept.
# Expected Result: Returns "yes" if an accepted taxonomy exists, otherwise "no".

chat_template_accepted_taxonomy_existance_check = ChatPromptTemplate.from_messages(
        [
            ("system", "You are the best ontology expert in the whole world with a particular interest in taxonomical classifications. You also know all about the \"{root_concept}\" concept. "),#\"{root_concept}\" concept's nature and 
            ("human", "Can you construct any accepted taxonomical classification with the root concept \"{root_concept}\"?{context} Answer only with just yes or no.")
        ]
    )

# CHECK EXISTENCE OF TAXONOMY CONTAINING TARGET SUB-CONCEPT
#
# Name: chat_template_super_taxonomy_existance_check
# Parameters: concept
# Description: Checks if the specified concept is part of any accepted taxonomy.
# Expected Result: Returns "yes" if the concept is part of an accepted taxonomy, otherwise "no".


chat_template_super_taxonomy_existance_check = ChatPromptTemplate.from_messages(
        [
            ("system", "You are the best ontology expert in the whole world with a particular interest in taxonomical classifications. You also possess all available knowledge about the \"{concept}\" concept. "),#\"{root_concept}\" concept's nature and
            ("human", "Is there any generally accepted taxonomical classification such that the concept \"{concept}\" is typically understood as the accepted element in this classification? Answer with just yes or no.")
        ]
    )

# FIND ROOT CONCEPT FOR TAXONOMY CONTAINING TARGET SUB-CONCEPT
#
# Name: chat_template_super_taxonomy_find
# Parameters: concept
# Description: Identifies the root concept of a taxonomy that contains the specified sub-concept.
# Expected Result: Returns the name of the root concept for the taxonomy that includes the given sub-concept.

chat_template_super_taxonomy_find = ChatPromptTemplate.from_messages(
        [
            ("system", "You are the best ontology expert in the whole world, with a particular interest in taxonomical classifications. You also possess all available knowledge about the \"{concept}\" concept. "),
            ("human", "The concept \"{concept}\" is typically considered an accepted concept in some unknown taxonomical classification. Use all your knowledge to find the name of the root concept for such taxonomy. This new concept must, at the same time, be the super-concept of the \"{concept}\" concept, and be the generally accepted root concept of some particular taxonomical classification. Skip explanations and return only the root concept's name.")
        ]
    )

# FIND TAXONOMICAL CLASSIFICATION CRITERIA FOR TAXONOMY WITH DEFINED ROOT CONCEPT
#
# Name: chat_template_find_taxonomical_criteria
# Parameters: root_concept, context
# Description: Identifies the most relevant differentiation criteria for classifying the root concept within a taxonomy.
# Expected Result: Returns a comma-separated list of taxonomical classification criteria.

chat_template_find_taxonomical_criteria = ChatPromptTemplate.from_messages(
        [
            ("system", "You are the best ontology expert in the whole world with a particular interest in the taxonomical classification and \"{root_concept}\" concept's nature."),
            ("human", "For the root concept \"{root_concept}\" provide the most generally accepted differentiation criteria for the taxonomical classification of \"{root_concept}\" root concept.{context} Skip explanations and return criteria in a comma-separated list like this: accepted criteria, another accepted criteria, another accepted criteria, etc.\n"),
            ("ai", "Criteria:")
        ]
    )

# FIND TAXONOMICAL RANKS FOR TAXONOMY WITH DEFINED ROOT CONCEPT AND SPECIFIC TAXONOMICAL CLASSIFICATION CRITERIA
#
# Name: chat_template_find_taxonomical_ranks
# Parameters: root_concept, criteria
# Description: Generates a list of taxonomical ranks for the specified root concept, using the provided classification criteria.
# Expected Result: Returns a comma-separated list of taxonomical ranks.

chat_template_find_taxonomical_ranks = ChatPromptTemplate.from_messages(
        [
            ("system", "You are the best ontology expert in the whole world. You have studied the \"{root_concept}\" concept's specifics for many years, and you know why it can not be so easily classified as many other concepts."),
 ("human", "The root concept of some unknown taxonomy is the \"{root_concept}\" concept. Your main purpose is to provide the best fitting distinctive and accepted taxonomical ranks (hierarchy levels) for such taxonomy. Those ranks list must be in the right order suitable for the correct classification of every \"{root_concept}\" root concept's subconcept. You must use the provided differentiation criteria list for the ranks discovery: {criteria}. Skip explanations and return ranks in a comma-separated list like this: accepted rank, another accepted rank, another accepted rank, etc."),
            ("ai", "Ranks for the \"{root_concept}\" concept classification:")
        ]
    )

# GENERATE SUB-CONCEPTS LIST FOR TARGET CONCEPT
#
# Name: chat_template_list_subconcepts
# Parameters: root_concept, concept, context_string, taxonomical_rank, taxonomical_context
# Description: Generates a list of sub-concepts for the specified concept, considering the given taxonomical rank and context.
# Expected Result: Returns a comma-separated list of relevant sub-concepts.

chat_template_list_subconcepts = ChatPromptTemplate.from_messages(
        [
            ("system", '''Role: You are the best Taxonomical Classification expert in the whole world. And also you possess all available knowledge about "{root_concept}" classification.
Instruction: Use all your knowledge, expertise, and context, to perform excellent sub-concepts list generation. You will be given context, information about the taxonomical rank of target sub-concepts, and information about the root concept of taxonomy and the currently processed concept. First, analyze all available data, identify all the sub-concepts of the target concept and taxonomical rank, choose among them concepts matching the current taxonomy, and choose exactly the {subconcepts_amount} best distinctive accurate and correct concepts among them. Then provide those chosen concepts as a response. 
Here is the relevant context: {context_string}
Constraints: All generated sub-concepts must be part of the "{taxonomical_rank}" taxonomical rank in the taxonomy. The root concept of the taxonomy is the "{root_concept}" super-concept. We are currently at the "{taxonomical_rank}" level in the hierarchy ({taxonomical_context}). Use this information, to better understand the broader taxonomical structure, and generate new concepts more accurately and effectively. 
             '''),
            ("human", "The root concept of the current taxonomy is {root_concept}. List only the most important subconcepts of \"{concept}\" in the context of \"{taxonomical_rank}\". Those subconcepts should be used for iterative taxonomy construction, so you must include ONLY sub-concepts that are only one level lower in the hierarchy than \"{concept}\" concept. Don't include instances of {concept}! Skip explanations and use a comma-separated format like this: important subconcept, another important subconcept, another important subconcept, etc.")
        ]
    )

# CHECK IF ALL CONCEPTS ARE TRUE SUB-CONCEPTS
#
# Name: chat_template_check_subconcepts
# Parameters: response, root_concept, taxonomical_rank
# Description: Validates if all concepts in the given response are true sub-concepts of the specified root concept.
# Expected Result: Returns "+" if all concepts are valid sub-concepts, otherwise "-".

chat_template_check_subconcepts = ChatPromptTemplate.from_messages(
        [
            ("system", '''You are an AI taxonomy checker. You possess great wisdom but are allowed to respond only either with + or - 
You must respond with - if the test fails, and with + if not. 
You must always respond to input queries..'''),
            ("human", "Check if all concepts in query: [{response}] are acceptable sub-concepts of the {root_concept} concept. You must fail and respond with - if they are incorrect sub-concepts (note that {root_concept} does not need to be mentioned directly in the response). If all concepts in the query are acceptable then respond with +")
        ]
    )

# DISCARD REDUNDANT SUB-CONCEPTS
#
# Name: chat_template_discard_subconcepts
# Parameters: root_concept, taxonomical_rank, taxonomical_context, candidate_list
# Description: Filters out redundant or incorrect sub-concepts from a provided list of candidates.
# Expected Result: Returns a comma-separated list of redundant sub-concepts.

chat_template_discard_subconcepts = ChatPromptTemplate.from_messages(
        [
            ("system", '''Role:
You are the best AI taxonomy expert in the world — a genius ontologist, who possesses all available knowledge about the {root_concept} nature and classification. 
Context:
Scientists are developing a new valuable {root_concept} taxonomical classification. They have formed the list of candidate terms. Some of them must be inserted as concepts into the current taxonomy. However, some other candidates are unnecessary or redundant and must be discarded.
Instruction:
You must diligently and painstakingly inspect every given candidate from that list. Your goal is to find all redundant subcategory candidates and make a complete list of them. So later other members of the crew would be able to filter them out. 
Discard not all concepts but only needless ones.
If there are no redundant sub-concepts in the provided list - leave response empty.
Use all your knowledge, expertise, and context to find and select all redundant and wrong subcategories from the given list. Non-selected candidates must be accurate and correct in the context of {root_concept} taxonomical classification and current taxonomical rank. Candidate term must be considered as redundant either if it is not a {root_concept} sub-category, or if it is not an acceptable sub-concept of current taxonomical rank (We are currently at the "{taxonomical_rank}" level in the hierarchy ({taxonomical_context})). '''),
            ("human", "The list of candidates is \"{candidate_list}\". Provide the list of redundant subconcepts in a comma-separated format like this: redundant subconcept, other redundant subconcept, another redundant subconcept, etc."),
            ("ai", "Redundant sub-concepts: ")
        ]
    )

# DISCARD REDUNDANT CRITERIA
#
# Name: chat_template_discard_criteria
# Parameters: root_concept, candidate_lists
# Description: Filters out redundant or incorrect criteria from a list of candidate criteria for classifying the root concept.
# Expected Result: Returns a comma-separated list of IDs of redundant criteria lists.

chat_template_discard_criteria = ChatPromptTemplate.from_messages(
        [
            ("system", '''Role:
You are the best AI taxonomy expert in the world - a genius ontologist, who possesses all available knowledge about the {root_concept} and their classification. 

Context:
Scientists are developing a new valuable {root_concept} taxonomical classification. Scientific groups have formed different lists, of the most generally accepted differentiation criteria for the {root_concept} classification. Some of them will be used for the construction of the taxonomical classification. However, some other lists are wrong or redundant and must be discarded.
You must diligently and painstakingly inspect every given list. Your goal is to find all redundant and unnecessary lists and mark them. So later other members of the crew would be able to filter them out. 

Instruction:
Use your expertise to find and select all redundant, unnecessary or just wrong lists. All non-selected candidates must be accurate and correct differentiation criteria for the taxonomical classification of {root_concept} particularly. The list must be considered redundant either if it is not a distinctive {root_concept} differentiation criteria list, or if it is not acceptable cause you as an ontology expert considered that list wrong. '''),
            ("human", "Candidates lists are \"{candidate_lists}\". Provide the IDs (ID count starts from 0) of redundant lists in a comma-separated format like this: unimportant list ID, other unimportant list ID, another unimportant list ID, etc."),
            ("ai", "Redundant list IDs: ")
        
        ]
    )

# OPTIMIZE TAXONOMICAL RANKS LISTS
#
# Name: chat_template_optimize_ranks_lists
# Parameters: root_concept, candidate_lists
# Description: Merges and refines multiple candidate lists of taxonomical ranks, removing redundancies and ensuring accurate classification.
# Expected Result: Returns semicolon-separated lists of optimized taxonomical ranks.

chat_template_optimize_ranks_lists = ChatPromptTemplate.from_messages(
        [
            ("system", '''Role:
Expert AI taxonomy specialist with extensive knowledge of various concepts.
Instructions:
Analyze several distinct candidate lists of taxonomical ranks, for the classification of some concepts, provided by different experts.
Try to correct mistakes made by those experts.
Exclude candidates that do not fit, add missing ones, and merge lists if needed.
Determine the most important and representative ranks of the given concept distinguishing it and its sub-concepts from other sub-concepts.
Merge the refined ranks from all lists into several, cohesive refined taxonomical ranks lists.
Present the final lists in a semicolon-separated format.
Context:
Root concept: {root_concept}
{candidate_lists}
Constraints:
Lists of ranks must be in a semicolon-separated format.
However, taxonomical ranks inside those lists must be in a comma-separated format.
No explanations are required in the output.
Each list includes only the highly relevant to the root concept ranks and could be used in the same hierarchy. 
The list must not contain synonymical ranks.
Ranks must be unique - each rank can appear only in one list.
Rank lists must be in the right order suitable for the correct iterative classification of all \"{root_concept}\" root concept's subconcepts. 
'''),
            ("human", "List accurate distinctive and accepted lists of taxonomical ranks (hierarchy levels) of {root_concept}. Skip explanations and return taxonomical ranks lists in a semicolon-separated format like this: relevant distinctive taxonomical ranks list; another relevant distinctive taxonomical ranks list; another relevant distinctive taxonomical ranks list; etc;")
        ]
    )

# POSTPROCESS SUB-CONCEPTS LIST FOR TARGET CONCEPT AND TAXONOMICAL RANK
#
# Name: chat_template_postprocess_subconcepts
# Parameters: root_concept, concept, context_string, taxonomical_rank, taxonomical_context
# Description: Refines and verifies the list of sub-concepts for the specified concept, ensuring they align with the given taxonomical rank and context.
# Expected Result: Returns a comma-separated list of true sub-concepts.

chat_template_postprocess_subconcepts = ChatPromptTemplate.from_messages(
        [
            ("system", '''Role: 
You are the best Taxonomical Classification assistant in the whole world. And also you possess all available knowledge about "{root_concept}".
Instruction:
Combine context provided, to perform excellent real sub-concepts list generation. You will be given the root concept, the taxonomical rank and the sub-concept candidates list.  You must correctly identify the true sub-concepts containing combined info. Skip explanations and use a comma-separated format like this: true subconcept, other true subconcept, another true subconcept, etc.
Examples: 
root concept: 'Software', taxonomical rank: 'User Interface Type', sub-concept candidates: 'GUI', 'CLI', 'VUI'. Provide the true sub-concepts.
Graphical User Interface (GUI) based Software, Command-Line Interface (CLI) Software, Software with Voice User Interface (VUI) support
root concept: 'Wound', taxonomical rank: 'Location', sub-concept candidates: 'Hands', 'Knees', 'Elbows'.  Provide the true sub-concepts.
Wounded Hand, Wounded Knee, Wounded Elbow '''),
            ("human", "root concept: '{root_concept}', taxonomical rank: '{taxonomical_rank}', sub-concept candidates: {subconcept_candidates}. Provide true sub-concepts."),
#            ("ai", "true sub-concepts: ")
        ]
    )
#__________________________________________________________________________________________________________________________________________

