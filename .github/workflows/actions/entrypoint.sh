#!/bin/sh

yum install -y udunits2-devel
PYTHONS=("cp37-cp37m" "cp38-cp38" "cp39-cp39")
WHEELHOUSE="/github/workspace/wheelhouse/"

export UDUNITS2_INCDIR="/usr/include/udunits2"
export UDUNITS2_LIBDIR="/usr/lib64"
export UDUNITS2_XML_PATH="/usr/share/udunits/udunits2.xml"

for PYTHON in ${PYTHONS[@]}; do
    /opt/python/${PYTHON}/bin/pip install --upgrade pip wheel setuptools setuptools_scm build twine auditwheel
    /opt/python/${PYTHON}/bin/python -m build --sdist --wheel . --outdir ${WHEELHOUSE}
done

for whl in ${WHEELHOUSE} cf_units*.whl; do
    auditwheel repair $whl
done
