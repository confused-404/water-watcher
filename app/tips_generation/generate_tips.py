import json
import os
import app.tips_generation.llm_utils as llm

def generate_tips():
    tips_file_path = "app/static/tips/saved_tips.json"
    
    if os.path.exists(tips_file_path):
        with open(tips_file_path, "r") as f:
            return json.load(f)
    else:
        model = llm.Model()
        
        with open("app/tips_generation/sys_prompt.txt", "r") as f:
            prompt = f.read()
        
        raw = model.generate(prompt)
        tips = [tip.strip() for tip in raw.split("\n") if tip.strip()]
        
        with open("app/static/tips/saved_tips.json", "w") as f:
            json.dump(tips, f)
        
        return tips
    
if __name__ == "__main__":
    print(generate_tips())