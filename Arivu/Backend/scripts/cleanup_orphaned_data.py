
import asyncio
import shutil
from pathlib import Path
from app.db.session import get_db
from app.db import crud
from app.core.config import settings

async def cleanup_orphaned():
    print("Checking for orphaned project directories...")
    
    # Get all project IDs from DB
    db_gen = get_db()
    db = await anext(db_gen)
    try:
        projects = await crud.list_projects(db)
        project_ids = {p.id for p in projects}
        print(f"Found {len(project_ids)} active projects in DB.")
    finally:
        await db.close()

    # Check data directory
    projects_dir = settings.data_dir / "projects"
    if not projects_dir.exists():
        print("No projects directory found.")
        return

    count = 0
    for child in projects_dir.iterdir():
        if child.is_dir() and child.name not in project_ids:
            print(f"Deleting orphaned directory: {child.name}")
            try:
                shutil.rmtree(child)
                count += 1
            except Exception as e:
                print(f"Failed to delete {child.name}: {e}")
    
    print(f"Cleaned up {count} orphaned directories.")

if __name__ == "__main__":
    asyncio.run(cleanup_orphaned())
