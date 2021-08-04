#!/usr/bin/env bash

trap 'echo "Aborted!"; exit 1' ERR
set -e


yum install -y udunits2-devel

PYTHONS=("cp37-cp37m" "cp38-cp38" "cp39-cp39")
WHEELHOUSE="/github/workspace/wheelhouse"
MANYLINUX="manylinux2014_x86_64"
DISTRIBUTION="dist"

export UDUNITS2_INCDIR="/usr/include/udunits2"
export UDUNITS2_LIBDIR="/usr/lib64"
export UDUNITS2_XML_PATH="/usr/share/udunits/udunits2.xml"

# Create the distribution directory.
mkdir ${DISTRIBUTION}

# Build the wheels in the wheelhouse.
for PYTHON in ${PYTHONS[@]}; do
    PYBIN="/opt/python/${PYTHON}/bin/python"
    ${PYBIN} -m pip install --upgrade pip wheel setuptools setuptools_scm build twine auditwheel
    ${PYBIN} -m build --wheel . --outdir ${WHEELHOUSE}
done

# Build the sdist in the distribution.
${PYBIN} -m build --sdist . --outdir ${DISTRIBUTION}

# Convert to manylinux wheels in the wheelhouse.
for BDIST_WHEEL in ${WHEELHOUSE}/cf_units*.whl; do
    auditwheel repair ${BDIST_WHEEL}
done

# Populate distribution with the manylinux wheels.
cp ${WHEELHOUSE}/cf_units*${MANYLINUX}.whl ${DISTRIBUTION}
