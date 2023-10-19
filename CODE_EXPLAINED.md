# Code explanation


## find_city()

Here we rely on spacy's natural language processing pipeline or nlp.
What this does essentially tokenise the text to produce a Doc object. 
The Doc is then processed (text is parsed, tags are added, entities are labelled and detected...).
When you call < nlp = en_core_web_sm.load() > we are telling the pipeline to work with the English language. 
When we then call doc = nlp(input_text), it processes the English text input (so tagging, parsing etc).

Then we check for GPE tag which stands for Geo Political Entity:  Countries, cities, states.
* Note: A named entity is a “real-world object” that's assigned a name – for example, a person, a country, a product or a book title. 
* SpaCy can recognize various types of named entities in a document, by asking the model for a prediction.

If the entity (so recognised text fragment) has the GPE associated tag we return the entity.text (so the entity name).