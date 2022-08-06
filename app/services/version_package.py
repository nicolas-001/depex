from app.services.db.database import version_collection


async def add_version(version_data: dict) -> dict:
    version = await version_collection.insert_one(version_data)
    new_version = await version_collection.find_one({"_id": version.inserted_id})
    return new_version