# This is a program meant to read in recipes from an old gelatin-based cookbook from the 70's
# I found via archive.org and generate new ones that are just as horrible to read about
# as the originals
import os
import openai
import pyttsx3

engine = pyttsx3.init()
vol = engine.getProperty('volume')
engine.setProperty('volume', vol - 0.25)
# Press the green button in the gutter to run the script.
openai.organization = os.environ['OPENAI_ORG']
openai.api_key = os.environ['OPENAI_ApI_KEY']
file_object = open("recipes.txt", "r")
data = file_object.read()

# make sure that we have the ability from generating an extra recipe unwanted
resp = openai.Completion.create(
    engine="davinci",
    max_tokens=265,
    prompt=data,
    temperature=0.5,
)

# split the response into separate lines for better parsing
resippy = list(filter(None, resp.choices[0].text.splitlines()))

found_recipe_name, found_ingredients_list, found_instructions = False, False, False
recipe_name = ""
inst_ind, ingr_ind = 0, 0
ingredients, instructions = [], []

# get the indexes of the separate parts of this recipe and its name
for s in range(0, len(resippy)):
    if resippy[s].startswith("RECIPE: ") and not found_recipe_name:
        recipe_name = resippy[s]
        found_recipe_name = True
    elif resippy[s].startswith("INGREDIENTS:") and not found_ingredients_list:
        ingr_ind = s
        found_ingredients_list = True
    elif resippy[s].startswith("INSTRUCTIONS:") and not found_instructions:
        inst_ind = s
        found_instructions = True

# Process the recipe name by removing the "RECIPE: " from the string we got
# Need to do this since we are gonna be making these into Text sources for OBS
unwanted_stuff_index = recipe_name.index(' ') + 1
recipe_name = recipe_name[unwanted_stuff_index:]

# now that we have the needed indexes, we create sublists from them to store the
# ingredients list and list of instructions
for i in range(ingr_ind, inst_ind):
    ingredients.append(resippy[i])

for i in range(inst_ind, len(resippy)):
    if resippy[i].startswith("RECIPE: "):
        break
    instructions.append(resippy[i])

file_names = ["recipe_name.txt", "ingredients.txt", "instructions.txt"]

# reassign the file object to write the response to their respective files
for i in range(0, 3):
    if i == 0:
        file_object = open(file_names[i], "w")
        file_object.write(recipe_name)
    elif i == 1:
        file_object = open(file_names[i], "w")
        for line in ingredients:
            file_object.writelines(line + '\n')
    else:
        file_object = open(file_names[i], "w")
        for line in instructions:
            file_object.writelines(line + '\n')

engine.say(recipe_name)
for s in ingredients:
    engine.say(s)
for line in instructions:
    engine.say(line)
engine.runAndWait()

# for safekeeping, write the whole of the response to file as well
# and close it too
file_object = open("generated_recipes.txt", "w")
file_object.write(resp.choices[0].text)
file_object.close()
