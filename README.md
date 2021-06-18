<h1 align="center" style="margin:1em;">
  <a href="https://scitools.org.uk/cf-units/docs/latest/">cf-units</a>
</h1>

<h4 align="center">
Units of measure as defined by the Climate and Forecast (CF) metadata
conventions.
</h4>

<p align="center">
<!-- https://shields.io/ is a good source of these -->
<a href="https://anaconda.org/conda-forge/cf-units">
<img src="https://img.shields.io/conda/dn/conda-forge/cf-units.svg"
 alt="conda-forge downloads" /></a>
<a href="https://github.com/SciTools/cf-units/releases">
<img src="https://img.shields.io/github/tag/SciTools/cf-units.svg"
 alt="Latest version" /></a>
<a href="https://github.com/SciTools/cf-units/commits/master">
<img src="https://img.shields.io/github/commits-since/SciTools/cf-units/latest.svg"
 alt="Commits since last release" /></a>
<a href="https://github.com/SciTools/cf-units/graphs/contributors">
<img src="https://img.shields.io/github/contributors/SciTools/cf-units.svg"
 alt="# contributors" /></a>
<a href="https://cirrus-ci.com/github/SciTools/cf-units">
<img src="https://api.cirrus-ci.com/github/SciTools/cf-units.svg?branch=master"
 alt="cirrus-ci" /></a>
<a href="https://codecov.io/gh/SciTools/cf-units">
<img src="https://codecov.io/gh/SciTools/cf-units/branch/master/graph/badge.svg?token=6LlYlyTUZG"
 alt="Coverage Status" /></a>
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
- [Credits, copyright and license](#credits--copyright-and-license)

<!-- tocstop -->

## Overview

Units of measure as required by the Climate and Forecast (CF) metadata
conventions.

Provision of a wrapper class to support Unidata/UCAR UDUNITS-2 library, and the
cftime calendar functionality.

Documentation can be found at <https://scitools.org.uk/cf-units/docs/latest/>.

### Example

    >>> from cf_units import Unit
    >>> km = Unit('kilometers')
    >>> m = Unit('meters')
    >>> m.convert(1500, km)
    1.5

## Get in touch

- Questions, ideas, general discussion or announcements
  of related projects: use the
  [Discussions space](https://github.com/SciTools/cf-units/discussions).
- Report bugs:
  [submit a GitHub issue](https://github.com/SciTools/cf-units/issues)
- Suggest features: see our [contributing guide](.github/CONTRIBUTING.md)


## Credits, copyright and license

cf-units is developed collaboratively under the SciTools umberella.

A full list of code contributors ("cf-units contributors") can be found at
https://github.com/SciTools/cf-units/graphs/contributors.

Code is just one of many ways of positively contributing to cf-units, please
see our [contributing guide](.github/CONTRIBUTING.md) for more details on how
you can get involved.

cf-units is released under a LGPL license with a shared copyright model.
See [COPYING](COPYING) and [COPYING.LESSER](COPYING.LESSER) for full terms.

The [Met Office](https://metoffice.gov.uk) has made a significant
contribution to the development, maintenance and support of this library.
All Met Office contributions are copyright on behalf of the British Crown.
