import os
import subprocess
DATABASE_URL = "postgresql://root:root@localhost/MovieDb"
OUTPUT_FILE = "models.py"

# Generate the raw SQLAlchemy models
subprocess.run(["sqlacodegen", DATABASE_URL, "--outfile", OUTPUT_FILE])

# Update models to use Flask-SQLAlchemy
with open(OUTPUT_FILE, "r") as f:
    content = f.read()

content = content.replace(
    "from sqlalchemy.ext.declarative import declarative_base",
    "from flask_sqlalchemy import SQLAlchemy\n\ndb = SQLAlchemy()"
).replace(
    "Base = declarative_base()",
    "Base = db.Model"
)

with open(OUTPUT_FILE, "w") as f:
    f.write(content)

print(f"Models generated and adapted for Flask in {OUTPUT_FILE}")
