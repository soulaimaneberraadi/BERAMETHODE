import os
import re

directories = ['components', 'src']
for directory in directories:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.tsx', '.ts')):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content
                
                # Replace } followed immediately by ; with }); IF it's part of a fetch call
                # But it's easier to just match: fetch( '/api/...' , { .... } <missing )> 
                content = re.sub(
                    r"(fetch\(['\"`]/api/[^'\"`]+['\"`],\s*\{.*?\})\s*([;\.])",
                    r"\1)\2",
                    content,
                    flags=re.DOTALL
                )
                
                # Additional case: where it is missing closing ) before .then
                content = re.sub(
                    r"(fetch\(['\"`]/api/[^'\"`]+['\"`],\s*\{.*?\})\s*\n\s*\.then",
                    r"\1)\n.then",
                    content,
                    flags=re.DOTALL
                )

                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Patched missing closing parenthesis in {filepath}")

print("Done fixing syntax.")
