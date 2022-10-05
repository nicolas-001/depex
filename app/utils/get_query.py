from bson import ObjectId

from copy import copy


async def get_complete_query(constraints: list[list[str]], package_id: ObjectId) -> dict:
    query: dict = {'$and': [{'package': {'$eq': package_id}}]}

    if constraints and constraints != 'any':
        for ctc in constraints:
            query['$and'].append(await get_partial_query(ctc))
    
    return query

async def get_partial_query(constraint: list[str]) -> dict:
    version = constraint[1]
    not_have_letters = version.replace('.', '').isdigit()
    number_of_points = version.count('.')
    number_of_elements = number_of_points + 1
    xyzd = await sanitize(version, number_of_points)

    match constraint[0]:
        case '=' | '==':
            query = await equal_query(xyzd)
        case '<':
            query = await less_than_query(xyzd, not_have_letters)
        case '>':
            query = await greater_than_query(xyzd, not_have_letters)
        case '>=':
            query = await greater_or_equal_than_query(xyzd, not_have_letters)
        case '<=':
            query = await less_or_equal_than_query(xyzd, not_have_letters)
        case '!=':
            query = await not_equal_query(xyzd)
        case '^':
            query = await approx_greater_than(xyzd, not_have_letters)
        case '~>' | '~=' | '~':
            query = await approx_greater_than_minor(xyzd, number_of_elements, not_have_letters)

    return query

async def sanitize(version: str, number_of_points: int) -> list[str]:
    match number_of_points:
        case 0:
            version += '.0.0.0'
        case 1:
            version += '.0.0'
        case 2:
            version += '.0'
    return version.split('.')

async def equal_query(xyzd: list[str]) -> dict:
    return {'$and': [
        {'mayor': {'$eq': xyzd[0]}},
        {'minor': {'$eq': xyzd[1]}},
        {'patch': {'$eq': xyzd[2]}},
        {'build_number': {'$eq': xyzd[3]}}
    ]}

async def greater_than_query(xyzd: list[str], not_have_letters: bool) -> dict:
    if not not_have_letters:
        return {'$or': [
            {'mayor': {'$gt': xyzd[0]}},
            {'$and': [{'mayor': {'$eq': xyzd[0]}}, {'minor': {'$gt': xyzd[1]}}]},
            {'$and': [{'mayor': {'$eq': xyzd[0]}}, {'minor': {'$eq': xyzd[1]}}, {'patch': {'$gt': xyzd[2]}}]},
            {'$and': [{'mayor': {'$eq': xyzd[0]}}, {'minor': {'$eq': xyzd[1]}}, {'patch': {'$eq': xyzd[2]}}, {'build_number': {'$gt': xyzd[3]}}]}
        ]}

    return {'$or': [
        {'mayor': {'$gt': xyzd[0]}},
        {'$and': [
            {'mayor': {'$eq': xyzd[0]}},
            {'$or': [{'minor': {'$gt': xyzd[1]}}, {'minor': {'$regex': xyzd[1]}}]}
        ]},
        {'$and': [
            {'mayor': {'$eq': xyzd[0]}},
            {'minor': {'$eq': xyzd[1]}},
            {'$or': [{'patch': {'$gt': xyzd[2]}}, {'patch': {'$regex': xyzd[2]}}]}
        ]},
        {'$and': [
            {'mayor': {'$eq': xyzd[0]}},
            {'minor': {'$eq': xyzd[1]}},
            {'patch': {'$eq': xyzd[2]}},
            {'$or': [{'build_number': {'$gt': xyzd[3]}}, {'build_number': {'$regex': xyzd[3]}}]}
        ]}
    ]}

async def less_than_query(xyzd: list[str], not_have_letters: bool) -> dict:
    if not not_have_letters:
        return {'$or': [
            {'mayor': {'$lt': xyzd[0]}}, 
            {'$and': [{'mayor': {'$eq': xyzd[0]}}, {'minor': {'$lt': xyzd[1]}}]}, 
            {'$and': [{'mayor': {'$eq': xyzd[0]}}, {'minor': {'$eq': xyzd[1]}}, {'patch': {'$lt': xyzd[2]}}]},
            {'$and': [{'mayor': {'$eq': xyzd[0]}}, {'minor': {'$eq': xyzd[1]}}, {'patch': {'$eq': xyzd[2]}}, {'build_number': {'$lt': xyzd[3]}}]}
        ]}

    return {'$or': [
        {'mayor': {'$gt': xyzd[0]}},
        {'$and': [
            {'mayor': {'$eq': xyzd[0]}},
            {'$or': [{'minor': {'$lt': xyzd[1]}}, {'minor': {'$regex': xyzd[1]}}]}
        ]},
        {'$and': [
            {'mayor': {'$eq': xyzd[0]}},
            {'minor': {'$eq': xyzd[1]}},
            {'$or': [{'patch': {'$lt': xyzd[2]}}, {'patch': {'$regex': xyzd[2]}}]}
        ]},
        {'$and': [
            {'mayor': {'$eq': xyzd[0]}},
            {'minor': {'$eq': xyzd[1]}},
            {'patch': {'$eq': xyzd[2]}},
            {'$or': [{'build_number': {'$lt': xyzd[3]}}, {'build_number': {'$regex': xyzd[3]}}]}
        ]}
    ]}

async def not_equal_query(xyzd: list[str]) -> dict:
    return {'$or': [
        {'mayor': {'$ne': xyzd[0]}},
        {'minor': {'$ne': xyzd[1]}},
        {'patch': {'$ne': xyzd[2]}},
        {'build_number': {'$ne': xyzd[3]}}
    ]}

async def greater_or_equal_than_query(xyzd: list[str], not_have_letters: bool) -> dict:
    return {'$or': [await equal_query(xyzd), await greater_than_query(xyzd, not_have_letters)]}

async def less_or_equal_than_query(xyzd: list[str], not_have_letters: bool) -> dict:
    return {'$or': [await equal_query(xyzd), await less_than_query(xyzd, not_have_letters)]}

async def approx_greater_than(xyzd: list[str], not_have_letters: bool) -> dict:
    up_xyzd = await get_up(xyzd)
    return {'$and': [await greater_or_equal_than_query(xyzd, not_have_letters), await less_than_query(up_xyzd, not_have_letters)]}

async def get_up(xyzd: list[str]) -> list[str]:
    for i in range(0, 4):
        if xyzd[i] != '0':
            up_xyzd = copy(xyzd)
            up_xyzd[i] = str(int(up_xyzd[i]) + 1)
            return up_xyzd
    return xyzd

async def approx_greater_than_minor(xyzd: list[str], number_of_elements: int, not_have_letters: bool) -> dict:
    up_xyzd = copy(xyzd)
    if number_of_elements != 1:
        up_xyzd[1] = str(int(up_xyzd[1]) + 1)
        return {'$and': [await greater_or_equal_than_query(xyzd, not_have_letters), await less_than_query(up_xyzd, not_have_letters)]}
    up_xyzd[0] = str(int(up_xyzd[0]) + 1)
    return {'$and': [await greater_or_equal_than_query(xyzd, not_have_letters), await less_than_query(up_xyzd, not_have_letters)]}