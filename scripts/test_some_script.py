# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "rich",
#     "boto3",
#     "awswrangler>=3.11.0",
#     "semver>=3.0.4",
# ]
# ///

import json
import os
import subprocess
import sys
from functools import cached_property

import awswrangler as wr
import boto3
import semver

PACKAGES_METADATA_EXCLUDE_NAMES = ["docker-stack", "apache-airflow-providers"]

def generate_packages_metadata():
    print("[info]Generating packages-metadata.json file\n")

    # if self.dry_run:
    #     get_console().print("Dry run enabled, skipping packages-metadata.json generation")
    #     return

    package_versions_map = {}
    s3_docs_path = "s3://live-docs-airflow-apache-org/docs/"
    resp = wr.s3.list_directories(s3_docs_path)
    print(resp)

    # package_path: s3://staging-docs-airflow-apache-org/docs/apache-airflow-providers-apache-cassandra/
    for package_path in resp:
        package_name = package_path.replace(s3_docs_path, "").rstrip("/")

        if package_name in PACKAGES_METADATA_EXCLUDE_NAMES:
            continue

        # version_path: s3://staging-docs-airflow-apache-org/docs/apache-airflow-providers-apache-cassandra/1.0.0/

        versions = [
            version_path.replace(package_path, "").rstrip("/")
            for version_path in wr.s3.list_directories(package_path)
            if version_path.replace(package_path, "").rstrip("/") != "stable"
        ]
        package_versions_map[package_name] = versions

    print(package_versions_map)

    all_packages_infos = dump_docs_package_metadata(package_versions_map)
    print(all_packages_infos)


def dump_docs_package_metadata(package_versions: dict[str, list[str]]):
    all_packages_infos = [
        {
            "package-name": package_name,
            "all-versions": (all_versions := get_all_versions(versions)),
            "stable-version": all_versions[-1],
        }
        for package_name, versions in package_versions.items()
    ]

    return all_packages_infos


def get_all_versions(versions: list[str]) -> list[str]:
    return sorted(
        versions,
        key=lambda d: semver.VersionInfo.parse(d),
    )


generate_packages_metadata()
