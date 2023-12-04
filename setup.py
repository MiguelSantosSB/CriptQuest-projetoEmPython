import cx_Freeze

executables = [cx_Freeze.Executable('main.py')]

cx_Freeze.setup(
    name="CriptQuest game",
    options={'build_exe': {'packages':['pygame'],
                           'include_files':['graphics','levels','scripts']}},
    
    executables = executables

)