import os
import sys
from pathlib import Path
from openai import OpenAI
import ollama
import pandas as pd
import json
import google.generativeai as genai
from dotenv import load_dotenv
from utils.token_count import count_tokens


load_dotenv()


# ----- OPENAI -----

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def openai_run(prompt, model_name="gpt-4.1-mini", temp=0.3) -> str:
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=temp,
    )
    return response.choices[0].message.content.strip()


# ------- GEMINI -------

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def gemini_run(prompt, model_name="gemini-2.5-flash", temp=0.3) -> str:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(
        prompt,
        generation_config={"temperature": temp}
    )
    return response.text.strip()




SUMMARY_PROMPT = f"""You are a medical summariser. Summarise the following text in a concise, clear way.
Focus on key features, symptoms, and treatment (avoid copying verbatim).

Text:
"""

DIAGNOSTIC_CRITERIA_PROMPT = f"""Extract Diagnostic Criteria for the mental health disorders from the following text. There can be one disorder or many.
Return in a json format like this:

Output:
[
    {{
        "disorder": "...",
        "criteria": "..."
    }},
    {{
        "disorder": "...",
        "criteria": "..."
    }},
]

Text:
"""



def read_text_file(file_path: str) -> str:
    """Read the contents of a text file."""
    return Path(file_path).read_text(encoding="utf-8")

def process_file(
    disease: str,
    isSummary: bool = True,
    isCriteria: bool = True,
    run_fn=None,
    summary_prompt: str = None,
    criteria_prompt: str = None,
) -> dict:
    """
    Process a disorder text file and return structured info.
    
    Args:
        file_path (str): path to txt file
        isSummary (bool): whether to summarise
        isCriteria (bool): whether to extract criteria
        run_fn (callable): function to call for LLM inference (e.g., openai_run, gemma_run, llama_run)
        summary_prompt (str): custom summary prompt (if None, uses default)
        criteria_prompt (str): custom diagnostic criteria prompt (if None, uses default)
    """
    if run_fn is None:
        raise ValueError("You must provide a run_fn (e.g., openai_run, gemma_run, llama_run).")

    file_path = f"docs/disorders/{disease}.txt"
    text = read_text_file(file_path)

    summary = ""
    criteria = ""

    if isSummary:
        prompt = (SUMMARY_PROMPT or summary_prompt or "Summarise this disorder text:\n") + text
        summary = run_fn(prompt)

    if isCriteria:
        prompt = (DIAGNOSTIC_CRITERIA_PROMPT or criteria_prompt or "Extract diagnostic criteria:\n") + text
        criteria = run_fn(prompt)

    return {
        "file": file_path,
        "summary": summary,
        "diagnostic_criteria": criteria,
        "input_tokens": count_tokens(prompt)
    }



summary = 0
criteria = 1
cap_size = 300
model_name = "gpt"
output_folder = "criteria_gpt2"

def main(run_one=None):
    diseases = [os.path.splitext(filename)[0] for filename in os.listdir("docs/disorders")]
    done_diseases = [os.path.splitext(filename)[0] for filename in os.listdir(f"docs/{output_folder}")]

    criteria_data = []
    summary_data = []
    count = 0

    for disease in diseases:
        # print(run_one, disease)
        if run_one and disease.lower().strip() != run_one.lower().strip():
            # print("Match")
            continue

        if count == cap_size:
            break

        if disease in done_diseases and not run_one:
            continue

        print(f"Starting {disease}")

        l = [disease]
        result = process_file(disease, summary, criteria, run_fn=openai_run)
        text = result["diagnostic_criteria"]
        # print("\n=== Summary ===")
        # print(result["summary"])
        # print("\n=== Diagnostic Criteria ===")
        # print(result["diagnostic_criteria"])

        if criteria:
            base_filename = f"docs/{output_folder}/{disease.strip()}"

            try:
                data = json.loads(text)
                json_file = Path(f"{base_filename}.json")
                with json_file.open("w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

            except json.JSONDecodeError:
                # Save as .txt
                txt_file = Path(f"{base_filename}.txt")
                with txt_file.open("w", encoding="utf-8") as f:
                    f.write(text)
                print(f"{disease} file not JSON Parsable")

            l += [base_filename, len(text), count_tokens(text)]
            criteria_data.append(l)

            print(f"Criteria Generated | Disease: {disease} | Characters: {len(text)} | Number of Input Tokens: {result['input_tokens']} | Number of Output Tokens: {count_tokens(text)}")

        if summary:
            output_txt = f"docs/{output_folder}/{disease.strip()}.txt"
            out_path = Path(output_txt)
            out_path.write_text(text, encoding="utf-8")

            l += [output_txt, len(text), count_tokens(text)]
            summary_data.append(l)

            print(f"Summary Generated | Disease: {disease} | Characters: {len(text)} | Number of Input Tokens: {result['input_tokens']} | Number of Output Tokens: {count_tokens(text)}")

        count += 1
        print("\n")

    # if len(criteria_data) > 0:
    #     criteria_data = pd.DataFrame(criteria_data)
    #     criteria_data.to_excel(f"docs/criteria_data_{model_name}.xlsx", index=False, header=["Disease", "Doc File Name", "Length", "Tokens"])

    # if len(summary_data) > 0:
    #     summary_data = pd.DataFrame(summary_data)
    #     summary_data.to_excel(f"docs/summary_data_{model_name}.xlsx", index=False, header=["Disease", "Doc File Name", "Length", "Tokens"])



if __name__ == "__main__":
    # print(DIAGNOSTIC_CRITERIA_PROMPT)
    main()



