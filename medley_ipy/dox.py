usage="""
Hybrid IPython / bash environment tailored for medley development.
  1) IPython extensions:
    fab-file integration:

    project manager:

      >>> proj.medley      # cd to src/storyville/medley
      >>> proj.ellington   # cd to src/storyville/ellington
      >>> proj.mtemplates  # cd to src/storyville/medley-templates

    shortcuts in webrowser (you can find more using tab completion):

      # opens up hudson's login window in a new tab
      >>> show.hudson.login

      # opens up munin's celery graphs for FE-5
      >>> show.munin.celery._5

  2) Extra completions:
    via ipy_git_completers:
      * git checkout <branch>
      * git <subcommand>
"""
