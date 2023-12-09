import cx_Freeze

executables = [cx_Freeze.Executable('CriptQuest.py')]

cx_Freeze.setup(
    name="CriptQuest",
    options={'build_exe': {'packages':['pygame'],
                           'include_files':['audio','graphics','levels','scripts']}},
    executables = executables

)


