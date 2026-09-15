import spacy
import json

# Load the English language model
nlp = spacy.load("en_core_web_sm")

# Case study text
text = """
Berners-Lee was born in London on 8 June 1955. Berners-Lee worked as an independent contractor at CERN from June to December 1980. While in Geneva, he proposed a project based on the concept of hypertext, to facilitate sharing and updating information among researchers.
"""

# Process the text with spaCy
doc = nlp(text)


# 1. Extract entities

entities = {}

for entity in doc.ents:
    entity_text = entity.text
    entity_type = entity.label_

    # Correct CERN's entity type
    if entity_text == "CERN":
        entity_type = "ORG"

    # Store unique entities
    entities[entity_text] = entity_type

# Add important concepts not detected as named entities
entities["project"] = "CONCEPT"
entities["hypertext"] = "CONCEPT"
entities["researchers"] = "GROUP"


# 2. Extract relations

relations = []


def add_relation(subject, relation, object_):
    """Add a relation if it does not already exist."""
    new_relation = {
        "subject": subject,
        "relation": relation,
        "object": object_
    }

    if new_relation not in relations:
        relations.append(new_relation)


# Process each sentence separately
for sentence in doc.sents:

    sentence_text = sentence.text

    # Birth information

    if "was born in" in sentence_text:
        parts = sentence_text.split("was born in", 1)

        subject = parts[0].strip()

        location_part = parts[1].strip()

        # Extract the location before "on"
        if " on " in location_part:
            location = location_part.split(" on ", 1)[0].strip()
            date = location_part.split(" on ", 1)[1].strip().rstrip(".")
        else:
            location = location_part.rstrip(".")
            date = None

        add_relation(subject, "bornIn", location)

        if date:
            add_relation(subject, "bornOn", date)


    # Employment information

    if "worked as an" in sentence_text and " at " in sentence_text:

        marker = "worked as an"

        subject, remaining = sentence_text.split(marker, 1)

        subject = subject.strip()
        remaining = remaining.strip()

        job = remaining.split(" at ", 1)[0].strip()

        remaining = remaining.split(" at ", 1)[1]

        organization = remaining.split(" from ", 1)[0].strip()

        add_relation(subject, "workedAs", job)
        add_relation(subject, "workedAt", organization)

        if " from " in remaining:
            period = remaining.split(" from ", 1)[1].strip().rstrip(".")
            add_relation(subject, "workedDuring", period)


    # Location information

    if "While in" in sentence_text:

        subject = sentence_text.split("While in", 1)[1]

        location = subject.split(",", 1)[0].strip()

        add_relation("Berners-Lee", "wasIn", location)


    # Project proposal

    if "proposed a project" in sentence_text:

        add_relation(
            "Berners-Lee",
            "proposed",
            "project"
        )


    # Project based on hypertext

    if "based on the concept of hypertext" in sentence_text:

        add_relation(
            "project",
            "basedOn",
            "hypertext"
        )


    # Information sharing

    if "among researchers" in sentence_text:

        add_relation(
            "project",
            "facilitatesInformationSharingAmong",
            "researchers"
        )


# 3. Create output

output = {
    "entities": [
        {
            "text": entity_text,
            "type": entity_type
        }
        for entity_text, entity_type in entities.items()
    ],
    "relations": relations
}


# 4. Save results to JSON

with open("outputs.json", "w", encoding="utf-8") as file:
    json.dump(output, file, indent=4, ensure_ascii=False)


# 5. Display results

print("ENTITIES")
print("--------")

for entity_text, entity_type in entities.items():
    print(f"{entity_text} -> {entity_type}")

print("\nRELATIONS")
print("---------")

for relation in relations:
    print(
        f"{relation['subject']} "
        f"--{relation['relation']}--> "
        f"{relation['object']}"
    )

print("\nResults saved to outputs.json")