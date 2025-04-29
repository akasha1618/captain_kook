import os
import streamlit as st
import openai
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session state for tracking
if 'recipes' not in st.session_state:
    st.session_state['recipes'] = []

st.title("🍽️ AI Recipe Generator & Tracker")

# Sidebar or main form for input
with st.form(key='recipe_form'):
    st.header("Enter Meal Preferences and Macronutrients")
    meal_type = st.selectbox(
        "Meal Type",
        options=["Breakfast", "Lunch", "Dinner", "Snack"],
        index=0
    )
    ingredients = st.text_area(
        "Ingredients You Have at Home",
        placeholder="e.g., eggs, spinach, tomatoes, cheese"
    )
    col1, col2 = st.columns(2)
    with col1:
        kcals    = st.number_input("Calories (kcal)", min_value=0, step=1)
    with col2:
        proteins = st.number_input("Protein target (g)", min_value=0.0, step=0.1)

    # Protein source selector
    st.markdown("**Choose primary protein source:**")
    protein_type = st.radio(
        "",
        options=["Chicken", "Beef", "Pork", "Tofu", "Beans", "Fish", "Eggs"],
        index=0,
        horizontal=True
    )
    custom_instructions = st.text_area(
        "Custom Instructions for the Recipe",
        placeholder="Add your custom instructions for the recipe"
    )
    submit = st.form_submit_button(label='Generate Recipe')

# Prompt template function
def build_prompt(meal_type, ingredients, kcals, proteins, protein_type, custom_instructions):
    prompt2 = (
    f"You are a professional, nutrition-focused recipe generator. "
    f"I want to prepare a {meal_type} that totals {kcals} kcal and {proteins} g protein, features {protein_type} as the primary protein source, and uses only these ingredients: {ingredients}. {custom_instructions}\n\n"
    "Instructions:\n"
    f"1. Select and quantify each ingredient (including cooking oil or extra ingredients used if that's the case) so total calories = {kcals} ± 5 kcal. Double-check your math.\n"
    f"2. Ensure {protein_type} provides a meaningful protein contribution.\n"
    "3. For every ingredient, report:\n"
    "- name\n"
    "- quantity (in grams or an appropriate unit)\n"
    "- unit\n"
    "- calories (fresh, raw values)\n"
    "- protein (g)\n"
    "4. Write minimal, clear cookingInstructions a home cook can follow.\n\n"
    "Rules:\n"
    "- Do not invent ingredients beyond available ingredients, oil, salt, pepper, and common spices—unless needed to hit the calorie target, in which case list them explicitly.\n"
    "- Return exactly one JSON object and nothing else.\n\n"
    "Output Format:\n"
    "```json\n"
    "{\n"
    "  \"meal\": \"<meal_type>\",\n"
    "  \"recipeName\": \"<brief descriptive title>\",\n"
    "  \"ingredients\": [\n"
    "    {\n"
    "      \"name\": \"<ingredient_name>\",\n"
    "      \"quantity\": <quantity>,\n"
    "      \"unit\": \"<unit>\",\n"
    "      \"calories\": <calories>,\n"
    "      \"protein\": <protein_grams>\n"
    "    }\n"
    "    // …repeat for each ingredient\n"
    "  ],\n"
    "  \"cookingInstructions\": \"<step-by-step instructions>\"\n"
    "}\n"
    "```"
)
    return prompt2



   ## prompt2 = (
   ##     f"Generate a detailed {meal_type.lower()} recipe." \
   ##     f" Use only the following ingredients that I have: {ingredients}." \
   ##     f" The recipe should meet approximately {kcals} kcal, {proteins}g protein, {carbs}g carbs, and {fats}g fats." \
   ##     f" {custom_instructions}" \
   ##     f"\n\nProvide the recipe in a clear format with title, ingredients list, instructions, and approximate nutrition per serving."
    ##)


# Handle submission
def generate_and_store_recipe():
    prompt = build_prompt(meal_type, ingredients, kcals, proteins, protein_type, custom_instructions)
    
    # Call OpenAI ChatCompletion
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=600
    )
    recipe_text = response.choices[0].message.content.strip()

    # Store in session state
    entry = {
        "timestamp": datetime.now().isoformat(),
        "meal_type": meal_type,
        "ingredients": ingredients,
        "kcals": kcals,
        "proteins": proteins,
        "protein type": protein_type,
        "custom_instructions": custom_instructions,
        "recipe": recipe_text
    }
    st.session_state['recipes'].append(entry)
    return recipe_text

# When user submits
if submit:
    if not ingredients:
        st.error("Please enter at least one ingredient.")
    else:
        with st.spinner('Generating your recipe...'):
            recipe = generate_and_store_recipe()
        st.success("Recipe generated!")
        st.markdown(f"### Your {meal_type} Recipe")
        st.write(recipe)

# Display history tracker
st.sidebar.header("📖 Recipe History")
for i, rec in enumerate(reversed(st.session_state['recipes']), 1):
    st.sidebar.write(f"**{i}. {rec['meal_type']}** at {rec['timestamp']}")
    st.sidebar.write(rec['recipe'][:100] + '...')
