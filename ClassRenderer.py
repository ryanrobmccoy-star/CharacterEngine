import json
import os
from jinja2 import Environment, FileSystemLoader

# -------------------------------
# Escape LaTeX special chars
# -------------------------------
def escape_latex(s):
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    return s

# -------------------------------
# Load JSON
# -------------------------------
def load_class_json(path):
    print(f"[LOAD] Attempting: {path}")
    if not os.path.exists(path):
        print("[ERROR] File does not exist!")
        return None
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"[LOAD SUCCESS] Keys: {list(data.keys())}")
    return data

# -------------------------------
# Render LaTeX using Jinja2
# -------------------------------
def render_class(class_json, template_file, output_tex):
    print("[RENDER] Initializing Jinja environment")
    env = Environment(
        loader=FileSystemLoader(searchpath="./templates"),
        autoescape=False
    )
    env.filters['latex'] = escape_latex

    print(f"[RENDER] Loading template: {template_file}")
    template = env.get_template(template_file)

    print("[RENDER] Rendering template...")
    tex_output = template.render(class_data=class_json)

    if not tex_output.strip():
        print("[WARNING] Rendered output is EMPTY!")

    print(f"[WRITE] Writing: {output_tex}")
    with open(output_tex, 'w', encoding='utf-8') as f:
        f.write(tex_output)

    print("[DONE] Render complete.\n")

# -------------------------------
# Main: Render class + subclasses
# -------------------------------
def main():
    classes_dir = "Classes"
    # Only process wizard for now
    class_folder = "wizard"
    class_path = os.path.join(classes_dir, class_folder, f"{class_folder}.json")

    class_json = load_class_json(class_path)
    if not class_json:
        print("[FATAL] Could not load class JSON.")
        return

    # Render main class
    output_tex = os.path.join(classes_dir, class_folder, f"{class_folder}.tex")
    render_class(class_json, "class_template.tex", output_tex)

    # Render subclasses if present
    subclasses_dir = os.path.join(classes_dir, class_folder, "subclasses")
    if os.path.exists(subclasses_dir):
        for subfile in os.listdir(subclasses_dir):
            if subfile.endswith(".json"):
                sub_path = os.path.join(subclasses_dir, subfile)
                sub_json = load_class_json(sub_path)
                if sub_json:
                    sub_tex = os.path.join(subclasses_dir, subfile.replace(".json", ".tex"))
                    render_class(sub_json, "class_template.tex", sub_tex)

    print("===== ALL RENDERED =====")

if __name__ == "__main__":
    main()
