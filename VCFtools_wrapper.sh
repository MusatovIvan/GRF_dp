#!/bin/bash

# Load version from the env file
VERSION=$(cat $SOFT/vcftools_version.env | cut -d'=' -f2)

if [[ "$1" == "--version" ]]; then
   echo "VCFtools $VERSION"
else
   /soft/vcftools-0.1.16/bin/vcftools "$@"
fi