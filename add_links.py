import os
import re

template_dir = r'c:\Users\ACER\OneDrive\Documentos\EPN\Septimo Semestre\Verificación y Validación de Software\Segundo Bimestre\Proyecto\Biblioteca-Digital\src\templates'
for root, _, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            
            # Sidebar Link Replacement
            new_content = new_content.replace('<a href="{% url \'colecciones:colecciones\' %}">Colecciones</a>', 
                                              '<a href="{% url \'colecciones:crear_coleccion\' %}">Crear colección</a>')
            
            # Additional Sidebar replacements (in case it had active class)
            new_content = new_content.replace('<a href="{% url \'colecciones:colecciones\' %}" class="activo">Colecciones</a>', 
                                              '<a href="{% url \'colecciones:crear_coleccion\' %}" class="activo">Crear colección</a>')

            # Text replacements
            new_content = new_content.replace('>Crear Libro<', '>Crear material<')
            new_content = new_content.replace('>Crear Material<', '>Crear material<')
            
            new_content = new_content.replace('>Crear Colección<', '>Crear colección<')
            new_content = new_content.replace('value="Crear Colección"', 'value="Crear colección"')
            new_content = new_content.replace('Crear Colección - Biblioteca', 'Crear colección - Biblioteca')
            
            new_content = new_content.replace('Nombre de la Colección', 'Nombre de la colección')
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated {filepath}')
