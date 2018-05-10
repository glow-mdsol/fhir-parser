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

logging.basicConfig()
logger = logging.getLogger(__name__)

_cache = 'downloads'


def infer_version(settings, default_url='http://hl7.org/fhir/index.html'):
    """
    Decorate the settings with the version/url/path_safe_version
    :param settings:
    :param default_url:
    """
    if not hasattr(settings, 'versioned_models'):
        # if you don't care about versioned models, lets make it so
        settings.versioned_models = False
    versions = fhirdirectory.get_versions()
    if hasattr(settings, 'specification_url'):
        for ver in versions:
            if settings.specification_url == ver.Link:
                settings.fhir_version = ver.Version
                settings.path_safe_version = ver.Version.replace('.', '_').replace(' ', '_')
    elif hasattr(settings, 'specification_version'):
        for ver in versions:
            if settings.specification_version == ver.Version:
                settings.specification_url = ver.Link
                settings.path_safe_version = ver.Version.replace('.', '_').replace(' ', '_')
    else:
        logger.warning("Need a specification_url or specification_version set, defaulting")
        for ver in versions:
            if default_url == ver.Link:
                settings.specification_url = ver.Link
                settings.specification_version = ver.Version
                settings.path_safe_version = ver.Version.replace('.', '_').replace(' ', '_')
        sys.exit(1)


if '__main__' == __name__:
    parser = argparse.ArgumentParser("Generate the FHIR Models")
    parser.add_argument("-f", default=False, action="store_true",
                        dest="force", help="Force rebuild of models")
    parser.add_argument("-d", "--dry-run", default=False, action="store_true", dest="dry",
                        help="Load and parse but not write resources")
    parser.add_argument("-l", "--load-only", default=False, action="store_true", dest="load_only",
                        help="Only Download the Specification")
    parser.add_argument("-s", "--settings", default='settings', action="store", dest="settings",
                        help="Specify what settings file to use")

    opts = parser.parse_args()

    if os.sep in opts.settings:
        _settings = opts.settings.replace(os.sep, '.')
    else:
        _settings = opts.settings

    # import the settings as requested
    settings = importlib.import_module(_settings)
    infer_version(settings)

    # assure we have all files
    loader = fhirloader.FHIRLoader(settings, _cache)
    spec_source = loader.load(opts.force)
    
    # parse
    if not opts.load_only:
        spec = fhirspec.FHIRSpec(spec_source, settings)
        if not opts.dry:
            spec.write()
