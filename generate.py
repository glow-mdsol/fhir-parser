#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Download and parse FHIR resource definitions
#  Supply "-f" to force a redownload of the spec
#  Supply "-d" to load and parse but not write resources
#  Supply "-l" to only download the spec

import sys

import settings
import fhirloader
import fhirspec
import argparse

_cache = 'downloads'


if '__main__' == __name__:
    parser = argparse.ArgumentParser("Generate the FHIR Models")
    parser.add_argument("-f", default=False, action="store_true", dest="force", help="Force rebuild of models")
    parser.add_argument(["-d", "--dry-run"], default=False, action="store_true", dest="dry",
                        help="Load and parse but not write resources")
    parser.add_argument(["-l", "--load-only"], default=False, action="store_true", dest="load_only",
                        help="Only Download the Specification")

    opts = parser.parse_args()

    # assure we have all files
    loader = fhirloader.FHIRLoader(settings, _cache)
    spec_source = loader.load(opts.force)
    
    # parse
    if not opts.load_only:
        spec = fhirspec.FHIRSpec(spec_source, settings)
        if not opts.dry:
            spec.write()
