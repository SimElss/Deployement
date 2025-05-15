import os
import subprocess

def compile_translations():
    languages = ['fr', 'en']
    for lang in languages:
        po_file = f'translations/{lang}/LC_MESSAGES/messages.po'
        mo_file = f'translations/{lang}/LC_MESSAGES/messages.mo'
        subprocess.run(['msgfmt', po_file, '-o', mo_file])

if __name__ == "__main__":
    compile_translations()