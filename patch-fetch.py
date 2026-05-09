import os
import re

directories = ['components', 'src']
for directory in directories:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.tsx', '.ts', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content
                
                # We need to replace fetch('/api/...') with fetch('/api/...', { credentials: 'include' })
                # And fetch('/api/...', { ... }) with fetch('/api/...', { credentials: 'include', ... })
                
                # Find all fetch calls that target /api/
                # Replace simple fetch without options
                content = re.sub(
                    r"fetch\((['\"`]/api/[^'\"`]+['\"`])\)",
                    r"fetch(\1, { credentials: 'include' })",
                    content
                )
                
                # Replace fetch with options block
                # Be careful not to replace if credentials: is already there
                def replacer(match):
                    url = match.group(1)
                    opts = match.group(2)
                    if 'credentials:' not in opts:
                        return f"fetch({url}, {{ credentials: 'include',{opts[1:]}"
                    return match.group(0)

                content = re.sub(
                    r"fetch\((['\"`]/api/[^'\"`]+['\"`])\s*,\s*(\{.*?\})\)",
                    replacer,
                    content,
                    flags=re.DOTALL
                )

                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Patched {filepath}")

print("Done scanning and patching components.")
