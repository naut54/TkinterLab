import sqlite3
from datetime import datetime

class TemplateManager:
    def __init__(self, db_file='templates.db'):
        self.db_file = db_file
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    code TEXT NOT NULL,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS template_tags (
                    template_id INTEGER,
                    tag TEXT,
                    FOREIGN KEY (template_id) REFERENCES templates (id),
                    PRIMARY KEY (template_id, tag)
                )
            ''')
            conn.commit()

    def add_template(self, name, code, description="", category="general", tags=None):
        try:
            with sqlite3.connect(self.db_file) as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO templates (name, description, code, category, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (name, description, code, category))
                
                template_id = c.lastrowid
                
                if tags:
                    c.executemany('''
                        INSERT INTO template_tags (template_id, tag)
                        VALUES (?, ?)
                    ''', [(template_id, tag) for tag in tags])
                
                conn.commit()
                return template_id
        except sqlite3.IntegrityError:
            raise ValueError("Una plantilla con ese nombre ya existe")

    def get_template(self, template_id):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT t.*, GROUP_CONCAT(tt.tag) as tags
                FROM templates t
                LEFT JOIN template_tags tt ON t.id = tt.template_id
                WHERE t.id = ?
                GROUP BY t.id
            ''', (template_id,))
            return c.fetchone()

    def get_all_templates(self, category=None):
        """
        Obtiene todas las plantillas, opcionalmente filtradas por categoría.
        
        Args:
            category (str, optional): Categoría para filtrar las plantillas.
        
        Returns:
            list: Lista de tuplas con la información de las plantillas.
                Cada tupla contiene: (id, name, description, code, category, created_at, updated_at, tags)
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            
            if category:
                query = '''
                    SELECT t.*, GROUP_CONCAT(tt.tag) as tags
                    FROM templates t
                    LEFT JOIN template_tags tt ON t.id = tt.template_id
                    WHERE t.category = ?
                    GROUP BY t.id
                    ORDER BY t.updated_at DESC
                '''
                c.execute(query, (category,))
            else:
                query = '''
                    SELECT t.*, GROUP_CONCAT(tt.tag) as tags
                    FROM templates t
                    LEFT JOIN template_tags tt ON t.id = tt.template_id
                    GROUP BY t.id
                    ORDER BY t.updated_at DESC
                '''
                c.execute(query)
            
            return c.fetchall()

    def get_templates_by_tag(self, tag):
        """
        Obtiene todas las plantillas que tienen un tag específico.
        
        Args:
            tag (str): Tag para filtrar las plantillas.
        
        Returns:
            list: Lista de tuplas con la información de las plantillas.
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            query = '''
                SELECT t.*, GROUP_CONCAT(tt2.tag) as tags
                FROM templates t
                INNER JOIN template_tags tt ON t.id = tt.template_id
                LEFT JOIN template_tags tt2 ON t.id = tt2.template_id
                WHERE tt.tag = ?
                GROUP BY t.id
                ORDER BY t.updated_at DESC
            '''
            c.execute(query, (tag,))
            return c.fetchall()

    def update_template(self, template_id, name=None, code=None, description=None, category=None, tags=None):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if code is not None:
                updates.append("code = ?")
                params.append(code)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if category is not None:
                updates.append("category = ?")
                params.append(category)
            
            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                query = f"UPDATE templates SET {', '.join(updates)} WHERE id = ?"
                params.append(template_id)
                c.execute(query, params)
                
                if tags is not None:
                    c.execute("DELETE FROM template_tags WHERE template_id = ?", (template_id,))
                    c.executemany('''
                        INSERT INTO template_tags (template_id, tag)
                        VALUES (?, ?)
                    ''', [(template_id, tag) for tag in tags])
                
                conn.commit()

    def delete_template(self, template_id):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM template_tags WHERE template_id = ?", (template_id,))
            c.execute("DELETE FROM templates WHERE id = ?", (template_id,))
            conn.commit()

    def get_all_tags(self):
        """
        Obtiene todos los tags únicos utilizados en las plantillas.
        
        Returns:
            list: Lista de strings con todos los tags únicos.
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute('SELECT DISTINCT tag FROM template_tags ORDER BY tag')
            return [row[0] for row in c.fetchall()]

    def get_all_categories(self):
        """
        Obtiene todas las categorías únicas utilizadas en las plantillas.
        
        Returns:
            list: Lista de strings con todas las categorías únicas.
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute('SELECT DISTINCT category FROM templates ORDER BY category')
            return [row[0] for row in c.fetchall()]