from bson import ObjectId

from datetime import datetime

from app.services.dbs.databases import version_collection


async def create_version(version_data: dict) -> dict:
    version = await version_collection.insert_one(version_data)
    new_version = await version_collection.find_one({'_id': version.inserted_id})
    return new_version

async def read_version_by_id(version_id: ObjectId) -> dict:
    version = await version_collection.find_one({'_id': version_id})
    return version

async def read_version_by_release_and_date(release: str, release_date: datetime) -> dict:
    version = await version_collection.find_one({'$and': [{'release': release}, {'release_date': release_date}]})
    return version

async def read_versions_by_query(query: dict) -> list:
    return [document['_id'] async for document in version_collection.find(query, {'_id': 1})]

async def update_version_package_edges(version_id: ObjectId, package_edges: list) -> dict:
    updated_version = await version_collection.find_one_and_update({'_id': version_id}, {'$set': {'package_edges': package_edges}})
    return updated_version

async def update_versions_cves_by_query(query: dict, cve_id: ObjectId) -> None:
    await version_collection.update_many(query, {'$push': {'cves': cve_id}})