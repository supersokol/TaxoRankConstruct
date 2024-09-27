# TaxoRankConstruct: A Methodology for Taxonomy Construction Using Large Language Models (LLMs)

This repository contains the code implementation for the TaxoRankConstruct methodology, designed to construct, refine, and expand taxonomies using Large Language Models (LLMs). The process is iterative, ensuring a balance between creativity, diversity, and accuracy. The repository utilizes three distinct models for generating, refining, and verifying taxonomical concepts.

## Table of Contents

- [Overview](#overview)
- [Model Initialization](#model-initialization)
- [Taxonomy Generation](#taxonomy-generation)
- [Iterative Concept Expansion](#iterative-concept-expansion)
- [Exporting and Evaluating the Taxonomy](#exporting-and-evaluating-the-taxonomy)
- [Usage](#usage)
- [Customization](#customization)
- [License](#license)

## Overview

TaxoRankConstruct is a flexible methodology that leverages LLMs to build hierarchical taxonomies. By combining the strengths of three distinct models, we achieve robust concept generation and refinement. The process consists of the following key steps:
1. Model Initialization
2. Taxonomy Generation
3. Iterative Concept Expansion
4. Export and Evaluation

## Model Initialization

The methodology begins by initializing three models, each with specific hyperparameters tailored to different stages of the taxonomy construction process:

- **Verification Model (`model_verify`)**  
  Based on the `gpt-4o-mini` architecture, this model ensures the accuracy and validity of generated concepts. It is configured with:
  - `temperature`: 0.9
  - `top_p`: 0.90
  - `presence_penalty`: 1.00
  - `frequency_penalty`: 0.00

- **Re-Generation Model (`model_re_generate`)**  
  Also based on the `gpt-4o-mini` architecture, this model focuses on regenerating and refining concepts. Configuration:
  - `temperature`: 1.40
  - `top_p`: 0.85
  - `presence_penalty`: 0.50
  - `frequency_penalty`: 1.00

- **New Concept Generation Model (`model_generate_new`)**  
  Using the `gpt-4o` architecture, this model generates creative new concepts for expanding the taxonomy. Configuration:
  - `temperature`: 1.40
  - `top_p`: 0.98
  - `presence_penalty`: 1.30
  - `frequency_penalty`: 1.40

These models are initialized with the `init_models` function and a session is started using the `start_session` function. You are encouraged to experiment with different hyperparameters to optimize performance for specific tasks.

## Taxonomy Generation

After model initialization, the taxonomy generation begins. The root concept (e.g., "Art") is defined, and the system constructs a taxonomy around it. Key parameters include:
- `definition_amount`: Number of definitions to generate.
- `definition_max_words`: Maximum word count for each definition.

Taxonomy generation is performed via the `create_taxonomy` function, which uses the three initialized models to iteratively build the hierarchy. For broader taxonomies that include the root concept as a sub-concept, the `create_super_taxonomy` function can be utilized (currently commented out in the example).

## Iterative Concept Expansion

Once the base taxonomy is built, the next step is iterative expansion. This phase generates new subconcepts and integrates them into the taxonomy. Expansion is guided by:
- `iteration_amm`: Maximum number of attempts to generate valid concepts.
- `max_words_context`: Maximum word count for the contextual description.
- `max_subconcept_length`: Maximum length of generated subconcepts.

The `iterate_level` function manages this process, ensuring that new concepts are both relevant and cohesive within the taxonomy structure.

## Exporting and Evaluating the Taxonomy

When the taxonomy is sufficiently developed, it can be exported to the **OWL (Web Ontology Language)** format for use in external tools and applications. This is done using the `export_to_owl` function. Additionally, the taxonomy structure and its content can be evaluated using the `info` method, which provides detailed insights into the taxonomy.

## Usage

To use the code for your own taxonomy construction tasks:
1. Clone this repository.
   ```bash
   git clone https://github.com/your-username/TaxoRankConstruct.git
   ```
2. Initialize the models and start a session:
   ```python
   from src.core.helper_functions import start_session, init_models
   log = start_session(api_key = api_key) 
   model_generate_new, model_re_generate, model_verify = init_models(log)
   ```
3. Generate the taxonomy:
   ```python
   from src.core.taxonomy_construction import construct_taxonomy
   tax_t = construct_taxonomy(root_concept, model_generate_new, model_re_generate, model_verify, log = log, check_existance = False)
   ```
4. Expand the taxonomy:
   ```python
   from src.core.taxonomy_construction import iterate_level
   tax_t = iterate_level(tax_t, 0, model_generate_new, model_re_generate, model_verify, log = log, iteration_amm = iteration_amm,  max_words_context = max_words_context, max_subconcept_lenght = max_subconcept_lenght)
   ```
5. Export the final taxonomy:
   ```python
   tax_t.export_to_owl()
   ```
6. Load taxonomy:
   ```python
   from src.core.helper_functions import load_taxonomy, Taxonomy
   loaded_tax = load_taxonomy(path)
   ```
7. Visualize the taxonomy:
   ```python
   from src.visualisation import visualize_taxonomy_as_graph_spaced
   generated_graph = visualize_taxonomy_as_graph_spaced(tax_t)
   ```

## Customization
You can modify various hyperparameters for the models and taxonomy generation process to suit your specific needs. Adjusting parameters like temperature, top_p, and penalty settings can lead to more creative or conservative outputs, depending on the task at hand.

## License
This project is licensed under the GPL-3.0 License. See the LICENSE file for details.
