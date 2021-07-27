pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'carnettty')


python3 = import('python3')

conf = configuration_data()
conf.set('PYTHON', python3.find_python().path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'carnettty.in',
  output: 'carnettty',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

carnettty_sources = [
  '__init__.py',
  'gi_composites.py',
  'carnet.py',
  'terminal-client/main.py',
  'terminal-client/listers/path_lister.py',
  'terminal-client/listers/latest_lister.py',
  'server/settings_manager.py',
  'server/notes/note_manager.py',
  'server/notes/note_manager.py',
  'server/databases/recent_db_manager.py',
  'server/databases/sync_db.py',
  'server/databases/keyword_db_manager.py',
  ]

install_data(carnettty_sources, install_dir: moduledir)
