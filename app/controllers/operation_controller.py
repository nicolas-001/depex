from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from flamapy.metamodels.dn_metamodel.operations import NetworkInfo
from flamapy.metamodels.smt_metamodel.transformations import NetworkToSMT
from flamapy.metamodels.smt_metamodel.operations import (
    ValidModel,
    NumberOfProducts,
    MinimizeImpact,
    MaximizeImpact,
    FilterConfigs,
    ValidConfig,
    CompleteConfig,
    ConfigByImpact
)

from app.services import (
    get_release_by_values,
    get_count_by_values
)
from app.utils import json_encoder

from .serialize_controller import serialize_graph

router = APIRouter()


@router.post('/operation/graph_info/{graph_id}', response_description='Graph info operation')
async def graph_info(graph_id: str) -> JSONResponse:
    dependency_graph = await serialize_graph(graph_id)
    operation = NetworkInfo()
    operation.execute(dependency_graph)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=json_encoder(operation.get_result())
    )


@router.post('/operation/valid_model/{graph_id}', response_description='Valid model operation')
async def valid_file(graph_id: str, agregator: str, file_name: str) -> JSONResponse:
    dependency_graph = await serialize_graph(graph_id)
    smt_transform = NetworkToSMT(dependency_graph, agregator)
    smt_transform.transform()
    smt_model = smt_transform.destination_model
    operation = ValidModel(file_name)
    operation.execute(smt_model)
    result = {'is_valid': operation.get_result()}
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_encoder(result))


@router.post(
    '/operation/number_of_products/{graph_id}',
    response_description='Number of products operation. Not use in huge graphs.'
)
async def number_of_products(graph_id: str, agregator: str, file_name: str) -> JSONResponse:
    dependency_graph = await serialize_graph(graph_id)
    smt_transform = NetworkToSMT(dependency_graph, agregator)
    smt_transform.transform()
    smt_model = smt_transform.destination_model
    operation = NumberOfProducts(file_name)
    operation.execute(smt_model)
    result = {'number_of_products': operation.get_result()}
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_encoder(result))


@router.post(
    '/operation/minimize_impact/{graph_id}',
    response_description='Minimize impact operation'
)
async def minimize_impact(
    graph_id: str,
    agregator: str,
    file_name: str,
    limit: int
) -> JSONResponse:
    dependency_graph = await serialize_graph(graph_id)
    smt_transform = NetworkToSMT(dependency_graph, agregator)
    smt_transform.transform()
    smt_model = smt_transform.destination_model
    operation = MinimizeImpact(file_name, limit)
    operation.execute(smt_model)
    result = await get_release_by_values(operation.get_result())
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_encoder({'result': result}))


@router.post(
    '/operation/maximize_impact/{graph_id}',
    response_description='Maximize impact operation'
)
async def maximize_impact(
    graph_id: str,
    agregator: str,
    file_name: str,
    limit: int
) -> JSONResponse:
    dependency_graph = await serialize_graph(graph_id)
    smt_transform = NetworkToSMT(dependency_graph, agregator)
    smt_transform.transform()
    smt_model = smt_transform.destination_model
    operation = MaximizeImpact(file_name, limit)
    operation.execute(smt_model)
    result = await get_release_by_values(operation.get_result())
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_encoder({'result': result}))


@router.post(
    '/operation/filter_configs/{graph_id}',
    response_description='Filter configs operation'
)
async def filter_configs(
    graph_id: str,
    agregator: str,
    file_name: str,
    max_threshold: float,
    min_threshold: float,
    limit: int
) -> JSONResponse:
    dependency_graph = await serialize_graph(graph_id)
    smt_transform = NetworkToSMT(dependency_graph, agregator)
    smt_transform.transform()
    smt_model = smt_transform.destination_model
    operation = FilterConfigs(file_name, max_threshold, min_threshold, limit)
    operation.execute(smt_model)
    result = await get_release_by_values(operation.get_result())
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_encoder({'result': result}))


@router.post(
    '/operation/valid_config/{graph_id}',
    response_description='Valid configuration operation'
)
async def valid_config(
    graph_id: str,
    agregator: str,
    file_name: str,
    config: dict[str, str]
) -> JSONResponse:
    dependency_graph = await serialize_graph(graph_id)
    smt_transform = NetworkToSMT(dependency_graph, agregator)
    smt_transform.transform()
    smt_model = smt_transform.destination_model
    operation = ValidConfig(file_name, await get_count_by_values(config))
    operation.execute(smt_model)
    result = {'is_valid': operation.get_result()}
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_encoder(result))


@router.post(
    '/operation/complete_config/{graph_id}',
    response_description='Complete configuration operation'
)
async def complete_config(
    graph_id: str,
    agregator: str,
    file_name: str,
    config: dict[str, str]
) -> JSONResponse:
    dependency_graph = await serialize_graph(graph_id)
    smt_transform = NetworkToSMT(dependency_graph, agregator)
    smt_transform.transform()
    smt_model = smt_transform.destination_model
    operation = CompleteConfig(file_name, await get_count_by_values(config))
    operation.execute(smt_model)
    result = await get_release_by_values(operation.get_result())
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_encoder({'result': result}))


@router.post(
    '/operation/config_by_impact/{graph_id}',
    response_description='Get a configuration by impact operation'
)
async def config_by_impact(
    graph_id: str,
    agregator: str,
    file_name: str,
    impact: float
) -> JSONResponse:
    dependency_graph = await serialize_graph(graph_id)
    smt_transform = NetworkToSMT(dependency_graph, agregator)
    smt_transform.transform()
    smt_model = smt_transform.destination_model
    operation = ConfigByImpact(file_name, impact)
    operation.execute(smt_model)
    result = await get_release_by_values(operation.get_result())
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_encoder({'result': result}))