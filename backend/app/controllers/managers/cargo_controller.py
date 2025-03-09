from asyncio import gather
from datetime import datetime, timedelta
from typing import Any

from app.apis import get_cargo_requires, get_cargo_versions
from app.controllers.cve_controller import attribute_cves
from app.services import (
    count_number_of_versions_by_package,
    create_package_and_versions,
    create_requirement_file,
    create_versions,
    read_cpe_product_by_package_name,
    read_package_by_name,
    read_versions_names_by_package,
    relate_packages,
    update_package_moment,
)


async def cargo_create_requirement_file(name: str, file: Any, repository_id: str) -> None:
    new_req_file_id = await create_requirement_file(
        {"name": name, "manager": "cargo", "moment": datetime.now()}, repository_id
    )
    await cargo_generate_packages(file["dependencies"], new_req_file_id)


async def cargo_generate_packages(
    dependencies: dict[str, str], parent_id: str, parent_version_name: str | None = None
) -> None:
    known_packages = []
    tasks = []
    for name, constraints in dependencies.items():
        package = await read_package_by_name("cargo", "none", name)
        if package:
            package["parent_id"] = parent_id
            package["parent_version_name"] = parent_version_name
            package["constraints"] = constraints
            if package["moment"] < datetime.now() - timedelta(days=10):
                await cargo_search_new_versions(package)
            known_packages.append(package)
        else:
            tasks.append(
                get_cargo_versions(
                    name,
                    constraints,
                    parent_id,
                    parent_version_name
                )
            )
    api_versions_results = await gather(*tasks)
    if api_versions_results:
        await cargo_create_package(api_versions_results)
    await relate_packages(known_packages)


async def cargo_create_package(
    api_versions_results: list[tuple[list[dict[str, Any]], str]]
) -> None:
    for all_versions, name, constraints, parent_id, parent_version_name in api_versions_results:
        if all_versions:
            cpe_product = await read_cpe_product_by_package_name(name)
            tasks = [
                attribute_cves(
                    version,
                    cpe_product,
                    "cargo"
                )
                for version in all_versions
            ]
            results = await gather(*tasks)
            new_versions = await create_package_and_versions(
                {"manager": "cargo", "group_id": "none", "name": name, "moment": datetime.now()},
                results,
                constraints,
                parent_id,
                parent_version_name,
            )
            tasks = [
                get_cargo_requires(
                    version["id"],
                    version["name"],
                    name
                )
                for version in new_versions
            ]
            api_requires_results = await gather(*tasks)
            await cargo_extract_packages(api_requires_results)


async def cargo_extract_packages(
    api_requires_results: list[tuple[dict[str, list[str] | str], str]]
) -> None:
    for require_packages, version_id, name in api_requires_results:
        await cargo_generate_packages(require_packages, version_id, name)


async def cargo_search_new_versions(package: dict[str, Any]) -> None:
    api_versions_results = await get_cargo_versions(package["name"])
    for all_versions in api_versions_results[0]:
        counter = await count_number_of_versions_by_package("cargo", "none", package["name"])
        if counter < len(all_versions):
            no_existing_versions: list[dict[str, Any]] = []
            cpe_product = await read_cpe_product_by_package_name(package["name"])
            actual_versions = await read_versions_names_by_package("cargo", "none", package["name"])
            for version in all_versions:
                if version["name"] not in actual_versions:
                    version["count"] = counter
                    new_version = await attribute_cves(
                        version, cpe_product, "cargo"
                    )
                    no_existing_versions.append(new_version)
                    counter += 1
            new_versions = await create_versions(
                package,
                no_existing_versions,
            )
            tasks = [
                get_cargo_requires(
                    version["id"],
                    version["name"],
                    package["name"]
                )
                for version in new_versions
            ]
            api_requires_results = await gather(*tasks)
            await cargo_extract_packages(api_requires_results)
    await update_package_moment("cargo", "none", package["name"])
