import json

from data import goals, teachers

db_data = {'goals': goals, 'teachers': teachers}

with open('db/goals_teachers.json', 'w', encoding='utf8') as db_file:
    json.dump(db_data, db_file, indent=4, ensure_ascii=False)

