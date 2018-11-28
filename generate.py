#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Download and parse FHIR resource definitions
#  Supply "-f" to force a redownload of the spec
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
                settings.specification_url = ver.Link
                settings.specification_version = ver.Version
                settings.path_safe_version = ver.Version.replace(".", "_").replace(
                    " ", "_"
                )
    return settings

if "__main__" == __name__:
    parser = argparse.ArgumentParser("Generate the FHIR Models")
    parser.add_argument(
        "-f",
        default=False,
        action="store_true",
        dest="force",
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

    if opts.list_only:
        versions = fhirdirectory.get_versions()
        for version in versions:
            print("{} - {}".format(version.Version, version.Description))
        sys.exit(0)
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

            # assure we have all files
            logger.info("Settings: Base URL: {} - Version: {}".format(settings.specification_url,
                                                                settings.specification_version))
            loader = fhirloader.FHIRLoader(settings, _cache)
            spec_source = loader.load(opts.force)

            # parse
            if not opts.load_only:
                spec = fhirspec.FHIRSpec(spec_source, settings)
                if not opts.dry:
                    spec.write()
            del settings
    else:
        settings = importlib.import_module(_settings)
        infer_version(settings)

        # set the destination path
        if opts.output:
            settings.target_base = opts.output

        # assure we have all files
        loader = fhirloader.FHIRLoader(settings, _cache)
        spec_source = loader.load(opts.force)

        # parse
        if not opts.load_only:
            spec = fhirspec.FHIRSpec(spec_source, settings)
            if not opts.dry:
                spec.write()
