import json
import re
import shutil
import os
from pathlib import Path

def clean_json_text(text: str) -> str:
    """Clean JSON text by fixing common issues like trailing commas or stray annotations."""
    # Remove BOM if present
    text = text.lstrip("\ufeff")

    # Remove annotations like ```json and ```
    text = re.sub(r"^```json", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r"```$", "", text.strip(), flags=re.MULTILINE)

    # Remove trailing commas before ] or }
    text = re.sub(r",(\s*[\]}])", r"\1", text)

    # Remove dangling commas or braces at end
    text = text.strip()
    if text.endswith(","):
        text = text[:-1]
    if text.endswith("},"):
        text = text[:-1] + "}"

    return text.strip()



def process_file(input_file: str, output_base: str, input_folder, output_folder):
    stored = [os.path.splitext(filename)[0] for filename in os.listdir(f"docs/{output_folder}")]
    if output_base in stored:
        print(f"File Already Stored.")
        return
    
    input_path = Path(f"docs/{input_folder}/{input_file}.txt")
    try:
        raw_text = input_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        json_inp_file = os.path.join(f"docs/{input_folder}", f"{input_file}.json")
        if os.path.exists(json_inp_file):
            json_out_file = os.path.join(f"docs/{output_folder}", f"{input_file}.json")
            shutil.copy(json_inp_file, json_out_file)
            print(f"File Already in JSON format. Copied to Destination Folder!")
            return
        else:
            print(f"File `{json_inp_file}` not found!")
            return


    try:
        cleaned_text = clean_json_text(raw_text)
        # print(cleaned_text)
        data = json.loads(cleaned_text)

        json_file = Path(f"docs/{output_folder}/{output_base}.json")
        with json_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    except json.JSONDecodeError as e:
        if 0 <= e.pos < len(cleaned_text):
            bad_char = cleaned_text[e.pos]
            print(f"Problematic character: {repr(bad_char)} (Unicode: U+{ord(bad_char):04X})")
            # Print surrounding context
            start = max(0, e.pos - 40)
            end = min(len(cleaned_text), e.pos + 40)
            print("Context around error:")
            print(cleaned_text[start:end])

    except Exception as e:
        print(f"Failed to parse JSON ({e}). Saved raw text: {output_base}")


def main(run_one=None):
    input_folder = "criteria_gpt2"
    output_folder = "criteria4"
    
    files = [os.path.splitext(filename)[0] for filename in os.listdir(f"docs/{input_folder}")]
    for file in files:
        if run_one and run_one.lower().strip() != file.lower().strip():
            continue
        process_file(file, file, input_folder, output_folder)


if __name__ == "__main__":
    main()
