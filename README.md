<h1 align="center" style="margin:1em;">
  <a href="https://scitools.org.uk/cf_units/docs/latest/">cf_units</a>
</h1>

<h4 align="center">
Units of measure as defined by the Climate and Forecast (CF) metadata
conventions.
</h4>

<p align="center">
<!-- https://shields.io/ is a good source of these -->
<a href="https://anaconda.org/conda-forge/cf_units">
<img src="https://img.shields.io/conda/dn/conda-forge/cf_units.svg"
 alt="conda-forge downloads" /></a>
<a href="https://github.com/SciTools/cf_units/releases">
<img src="https://img.shields.io/github/tag/SciTools/cf_units.svg"
 alt="Latest version" /></a>
<a href="https://github.com/SciTools/cf_units/commits/master">
<img src="https://img.shields.io/github/commits-since/SciTools/cf_units/latest.svg"
 alt="Commits since last release" /></a>
<a href="https://github.com/SciTools/cf_units/graphs/contributors">
<img src="https://img.shields.io/github/contributors/SciTools/cf_units.svg"
 alt="# contributors" /></a>
<a href="https://travis-ci.org/SciTools/cf_units/branches">
<img src="https://api.travis-ci.org/repositories/SciTools/cf_units.svg?branch=master"
 alt="Travis-CI" /></a>
<!-- <a href="https://zenodo.org/badge/latestdoi/5282596">
<img src="https://zenodo.org/badge/5282596.svg"
 alt="zenodo" /></a> -->
</p>
<br>

# Table of contents

<!--
NOTE: toc auto-generated with https://github.com/jonschlinkert/markdown-toc
    $> markdown-toc -i --bullets='-' README.md

NOTE: This entire README can be markdown linted with
    https://github.com/igorshubovych/markdownlint-cli
    $ echo '{"no-inline-html": false}' > .markdownrc
    $ markdownlint README.md
-->

<!-- toc -->

- [Overview](#overview)
  - [Example](#example)
- [Get in touch](#get-in-touch)
- [License and copyright](#license-and-copyright)

<!-- tocstop -->

## Overview

Units of measure as required by the Climate and Forecast (CF) metadata
conventions.

Provision of a wrapper class to support Unidata/UCAR UDUNITS-2 library, and the
cftime calendar functionality.

Documentation can be found at <https://scitools.org.uk/cf_units/docs/latest/>.

### Example

    >>> from cf_units import Unit
    >>> km = Unit('kilometers')
    >>> m = Unit('meters')
    >>> m.convert(1500, km)
    1.5

## Get in touch

- Questions, ideas, general discussion or announcements
  of related projects use the
  [Google Group](https://groups.google.com/forum/#!forum/scitools-iris).
- Report bugs, suggest features or view the source code on
  [GitHub](https://github.com/SciTools/cf_units).

## License and copyright

Cartopy is licensed under GNU Lesser General Public License (LGPLv3).

Development occurs on GitHub at <https://github.com/SciTools/cf_units>, with a
contributor's license agreement (CLA) that can be found at
<https://scitools.org.uk/governance.html>.

(C) British Crown Copyright, Met Office
