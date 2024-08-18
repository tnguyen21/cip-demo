import openai
import numpy as np
import pandas as pd
import os

def construct_hewitt_et_al_prompt(
    political_leaning,
    age,
    ethnicity,
    gender,
    education_level,
    party,
    policy
):
    """
    construct a prompt approximately based on work by Hewitt Et Al.
     https://docsend.com/view/qeeccuggec56k9hd
    """
    prompt = f"""
You are a {political_leaning}, {age}, {ethnicity}, {gender}, Londoner with {education_level}, who identifies as {party}.
You are asked about your thoughts on the following policy for the Greater Londer Area:

{policy}

Please concisely explain how you feel about the policy.
"""
    return prompt

def generate_dummy_data():
    # Example distributions
    # All of these numbers are dummy numbers until we find some stats to be confident in!
    political_leaning_dist = ['Liberal', 'Conservative', 'Moderate']
    political_leaning_prob = [0.4, 0.3, 0.3]

    age_dist = np.arange(18, 90)
    age_prob = np.random.normal(50, 15, len(age_dist))
    age_prob = age_prob / age_prob.sum()  # Normalize to sum to 1

    ethnicity_dist = ['White', 'Black', 'Asian', 'Hispanic', 'Other']
    ethnicity_prob = [0.6, 0.13, 0.06, 0.18, 0.03]

    gender_dist = ['Male', 'Female', 'Other']
    gender_prob = [0.49, 0.49, 0.02]

    education_level_dist = ['High School', 'Some College', 'Bachelor', 'Master', 'PhD']
    education_level_prob = [0.3, 0.3, 0.2, 0.15, 0.05]

    party_dist = ['Labour', 'Conservative', 'Liberal Democrat', 'Other']
    party_prob = [0.4, 0.35, 0.2, 0.05]# Example: Add 10 rows to the DataFrame
    rows = []
    for _ in range(10):
        row = {
            'political_leaning': np.random.choice(political_leaning_dist, p=political_leaning_prob),
            'age': np.random.choice(age_dist, p=age_prob),
            'ethnicity': np.random.choice(ethnicity_dist, p=ethnicity_prob),
            'gender': np.random.choice(gender_dist, p=gender_prob),
            'education_level': np.random.choice(education_level_dist, p=education_level_prob),
            'party': np.random.choice(party_dist, p=party_prob)
        }
        rows.append(row)

    df = pd.DataFrame(rows, columns=['political_leaning', 'age', 'ethnicity', 'gender', 'education_level', 'party'])
    df_dict = df.to_dict(orient='records')
    
    return df_dict


def generate_responses(policy):
    responses = []
    client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
    
    df_dict = generate_dummy_data()
    
    for row in df_dict:
        prompt = construct_hewitt_et_al_prompt(
            row['political_leaning'],
            row['age'],
            row['ethnicity'],
            row['gender'],
            row['education_level'],
            row['party'],
            policy
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt},]
        )
        responses.append((row, response.choices[0].message.content))  

    return responses