python_sources = [
  '__init__.py',
  'config.py',
  'tex.py',
  'util.py',
]

py.install_sources(
  python_sources,
  pure: false,
  subdir: 'cf_units'
)

udunits2 = dependency('udunits')

py.extension_module(
    '_udunits2',
    ['_udunits2.pyx'],
    dependencies: [udunits2],
    install: true,
    subdir: 'cf_units'
)

subdir('tests')
subdir('_udunits2_parser')
