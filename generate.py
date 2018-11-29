#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Download and parse FHIR resource definitions
#  Supply "-f" to force a redownload of the spec
#  Supply "-c" to force using the cached spec (incompatible with "-f")
#  Supply "-d" to load and parse but not write resources
#  Supply "-l" to only download the spec

import importlib
import os
import sys

import fhirloader
import fhirspec
import argparse
import fhirdirectory
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

_cache = "downloads"


def infer_version(settings, default_url="http://hl7.org/fhir/index.html"):
    """
    Decorate the settings with the version/url/path_safe_version
    :param settings:
    :param default_url:
    """
    if not hasattr(settings, "versioned_models"):
        # if you don't care about versioned models, let's make it so
        settings.versioned_models = False
    # Download the version information
    versions = fhirdirectory.get_versions()
    if hasattr(settings, "specification_url"):
        logger.info(
            "Using Specification URL Value {}".format(settings.specification_url)
        )
        for ver in versions:
            if settings.specification_url == ver.Link:
                logger.info(
                    "Found Specification URL {} with version {}".format(
                        settings.specification_url, ver.Version
                    )
                )
                settings.sequence = ver.Sequence
                settings.fhir_version = ver.Version
                settings.path_safe_version = ver.Version.replace(".", "_").replace(
                    " ", "_"
                )
    elif hasattr(settings, "specification_version"):
        logger.info(
            "Using Specification Version Value {}".format(
                settings.specification_version
            )
        )
        for ver in versions:
            if settings.specification_version == ver.Version:
                logger.info(
                    "Found Specification Version Value {} at URL {}".format(
                        settings.specification_version, ver.Link
                    )
                )

                settings.sequence = ver.Sequence
                settings.specification_url = ver.Link
                settings.path_safe_version = ver.Version.replace(".", "_").replace(
                    " ", "_"
                )
    else:
        logger.warning(
            "Need a specification_url or specification_version set, defaulting"
        )
        for ver in versions:
            if default_url == ver.Link:
                settings.sequence = ver.Sequence
                settings.specification_url = ver.Link
                settings.specification_version = ver.Version
                settings.path_safe_version = ver.Version.replace(".", "_").replace(
                    " ", "_"
                )
    return settings


def execute_process(force_download, force_cache, load_only, dry, settings):
    loader = fhirloader.FHIRLoader(settings, _cache)
    spec_source = loader.load(force_download=force_download, force_cache=force_cache)

    # parse
    if not load_only:
        spec = fhirspec.FHIRSpec(spec_source, settings)
        if not dry:
            spec.write()


if "__main__" == __name__:
    parser = argparse.ArgumentParser("Generate the FHIR Models")
    parser.add_argument(
        "-f",
        default=False,
        action="store_true",
        dest="force_download",
        help="Force rebuild of models",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        default=False,
        action="store_true",
        dest="dry",
        help="Load and parse but not write resources",
    )
    parser.add_argument(
        "-c",
        "--cache-only",
        default=False,
        action="store_true",
        dest="force_cache",
        help="force using the cached spec (incompatible with \"-f\")",
    )
    parser.add_argument(
        "-l",
        "--load-only",
        default=False,
        action="store_true",
        dest="load_only",
        help="Only Download the Specification",
    )
    parser.add_argument(
        "-s",
        "--settings",
        default="Default/settings",
        action="store",
        dest="settings",
        help="Specify what settings file to use",
    )
    parser.add_argument(
        "-o",
        "--output-location",
        action="store",
        dest="output",
        help="Specify the output location",
    )
    parser.add_argument(
        "-v",
        "--versions",
        action="store",
        nargs="*",
        metavar="VERSION",
        dest="versions",
        default=[],
        help="Specify the versions to generate",
    )
    parser.add_argument(
        "-p",
        "--print-versions",
        default=False,
        action="store_true",
        dest="list_only",
        help="List versions in the directory",
    )

    opts = parser.parse_args()

    if opts.force_download and opts.force_cache:
        print("Can't Force Redownload and Use cache only")
        sys.exit(1)
    if opts.list_only:
        versions = fhirdirectory.get_versions()
        for version in versions:
            print("{} - {}".format(version.Version, version.Description))
        sys.exit(0)

    # Turn a Path into a Module
    if os.sep in opts.settings:
        _settings = opts.settings.replace(os.sep, ".")
    else:
        _settings = opts.settings

    if len(opts.versions) > 0:
        # iterate over requested versions
        for version in opts.versions:
            # import the settings as requested
            settings = importlib.import_module(_settings)
            # overwrite the version
            settings.specification_version = version
            # turn the version into a URI
            settings = infer_version(settings)

            # set the destination path
            if opts.output:
                # overwrite the target_base to point the output elsewhere
                settings.target_base = opts.output
            execute_process(force_download=opts.force_download,
                            force_cache=opts.force_cache,
                            dry=opts.dry,
                            load_only=opts.load_only,
                            settings=settings)
            # assure we have all files
            del settings
    else:
        settings = importlib.import_module(_settings)
        infer_version(settings)

        # set the destination path
        if opts.output:
            settings.target_base = opts.output

        # assure we have all files
        execute_process(force_download=opts.force_download,
                        force_cache=opts.force_cache,
                        dry=opts.dry,
                        load_only=opts.load_only,
                        settings=settings)
