from typing import Any

from fastapi import HTTPException

from .dbs.databases import get_graph_db_session


async def create_repositories(repository: dict[str, Any]) -> dict[str, str]:
    repository_ids: dict[str, str] = {}
    query = '''
    create(r: Repository{
        owner: $owner,
        name: $name,
        add_extras: $add_extras,
        is_complete: $is_complete
    })
    return elementid(r) as id
    '''
    pip_session, npm_session, mvn_session = get_graph_db_session('ALL')
    pip_result = await pip_session.run(query, repository)
    pip_record = await pip_result.single()
    repository_ids.update({'PIP': pip_record[0]})
    npm_result = await npm_session.run(query, repository)
    npm_record = await npm_result.single()
    repository_ids.update({'NPM': npm_record[0]})
    mvn_result = await mvn_session.run(query, repository)
    mvn_record = await mvn_result.single()
    repository_ids.update({'MVN': mvn_record[0]})
    return repository_ids


async def read_repository_by_owner_name(
    owner: str,
    name: str,
    package_manager: str
) -> dict[str, Any]:
    query = '''
    match(r: Repository{owner: $owner, name: $name}) return elementid(r)
    '''
    session = get_graph_db_session(package_manager)
    result = await session.run(query, owner=owner, name=name)
    record = await result.single()
    return record[0] if record else None


async def read_repository_files(repository_id: str, package_manager: str) -> list[dict[str, Any]]:
    query = '''
    match(r: Repository)-[*1]->(s:RequirementFile) where elementid(r) = $repository_id return s{.*}
    '''
    session = get_graph_db_session(package_manager)
    result = await session.run(query, repository_id=repository_id)
    record = await result.single()
    return record[0] if record else None


async def read_graph_by_repository_id(
    requirement_file_id: str,
    package_manager: str
) -> dict[str, Any]:
    query = '''
    match (rf: RequirementFile) where elementid(rf) = $requirement_file_id
    call apoc.path.subgraphAll(rf, {relationshipFilter: '>'}) yield nodes, relationships
    return nodes, relationships
    '''
    session = get_graph_db_session(package_manager)
    result = await session.run(query, requirement_file_id=requirement_file_id)
    record = await result.single()
    if record:
        return record[0]
    raise HTTPException(status_code=404, detail=[f'Graph with id {requirement_file_id} not found'])


async def read_data_for_smt_transform(
    requirement_file_id: str,
    package_manager: str
) -> dict[str, Any]:
    query = '''
    match (rf: RequirementFile) where elementid(rf) = $requirement_file_id
    call apoc.path.subgraphAll(rf, {relationshipFilter: '>'}) yield relationships
    unwind relationships as relationship
    with case type(relationship)
    when 'REQUIRES'  then {
        parent_type: labels(startnode(relationship))[0],
        parent_id: elementid(startnode(relationship)),
        parent_name: startnode(relationship).name,
        parent_count: startnode(relationship).count,
        dependency: endnode(relationship).name,
        constraints: relationship.constraints
    }
    end as requires,
    case type(relationship)
    when 'HAVE' then {
        dependency: startnode(relationship).name,
        id: elementid(endnode(relationship)),
        release: endnode(relationship).name,
        count: endnode(relationship).count,
        mean: endnode(relationship).mean,
        weighted_mean: endnode(relationship).weighted_mean
    }
    end as have
    return {requires: collect(requires), have: collect(have)}
    '''
    session = get_graph_db_session(package_manager)
    result = await session.run(query, requirement_file_id=requirement_file_id)
    record = await result.single()
    return record[0] if record else None


async def update_repository_is_completed(repository_id: str, package_manager: str) -> None:
    query = '''
    match (r: Repository) where elementid(r) = $repository_id
    set r.is_complete = true
    '''
    session = get_graph_db_session(package_manager)
    await session.run(query, repository_id=repository_id)