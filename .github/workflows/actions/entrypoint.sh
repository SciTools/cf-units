#!/bin/sh

yum install -y udunits2-devel
PYTHONS=("cp36-cp36m" "cp37-cp37m" "cp38-cp38" "cp39-cp39")

cp /usr/include/udunits2/* /usr/include/

SITECFG=cf_units/etc/site.cfg
echo "[System]" > $SITECFG
echo "udunits2_xml_path = /usr/share/udunits/udunits2.xml" >> $SITECFG

for PYTHON in ${PYTHONS[@]}; do
    /opt/python/${PYTHON}/bin/pip install --upgrade pip wheel setuptools setuptools_scm build twine auditwheel
    /opt/python/${PYTHON}/bin/python -m build --sdist --wheel . --outdir /github/workspace/wheelhouse/
done

for whl in /github/workspace/wheelhouse/cf_units*.whl; do
    auditwheel repair $whl
done
