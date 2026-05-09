import os
import re

directories = ['src/components']
for directory in directories:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.tsx', '.ts')):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content
                
                # Fix JSON.stringify({ ... }, \n }); -> JSON.stringify({ ... }), \n });
                content = re.sub(
                    r"body: JSON\.stringify\((\{.*?\}),(\n\s*\}\)?)",
                    r"body: JSON.stringify(\1),\2",
                    content,
                    flags=re.DOTALL
                )

                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Patched JSON.stringify syntax in {filepath}")

print("Done scanning and patching JSON syntax errors.")
