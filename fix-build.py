import re

# Fix App.tsx
with open('App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace("credentials: 'include', credentials: 'include'", "credentials: 'include'")
with open('App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix Profil.tsx
with open('components/Profil.tsx', 'r', encoding='utf-8') as f:
    p_content = f.read()
p_content = p_content.replace("await fetch('/api/setup-admin', { credentials: 'include', method: 'POST' };", "await fetch('/api/setup-admin', { credentials: 'include', method: 'POST' });")
with open('components/Profil.tsx', 'w', encoding='utf-8') as f:
    f.write(p_content)

print("Fixed App.tsx and Profil.tsx")
