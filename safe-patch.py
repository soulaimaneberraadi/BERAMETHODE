import os
import re

directories = ['components', 'src', '.']

for directory in directories:
    if directory == '.':
        files_to_check = ['App.tsx']
        roots = [('.', [], files_to_check)]
    else:
        roots = os.walk(directory)

    for root, dirs, files in roots:
        for file in files:
            if file.endswith(('.tsx', '.ts')):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                orig = content
                
                # We want to skip if already patched but since we git checkout it's clean
                
                # Rule 1: fetch('/api/foo') -> fetch('/api/foo', { credentials: 'include' })
                content = re.sub(
                    r"fetch\((['\"`]/api/[^'\"`]+['\"`])\)",
                    r"fetch(\1, { credentials: 'include' })",
                    content
                )

                # Rule 2: fetch('/api/foo', { ... }) -> insert at $\{
                # We match fetch( URL , {
                content = re.sub(
                    r"fetch\((['\"`]/api/[^'\"`]+['\"`])\s*,\s*\{",
                    r"fetch(\1, { credentials: 'include', ",
                    content
                )

                # Deduplicate if it already existed
                content = content.replace("credentials: 'include', credentials: 'include',", "credentials: 'include',")
                content = content.replace("credentials: 'include',  credentials: 'include',", "credentials: 'include',")

                if content != orig:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Patched neatly {path}")

print("Done patching.")
