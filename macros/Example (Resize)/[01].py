# PAL DV 4:3 - 59:54
# above 'PAL DV 4:3 - 59:54' will be the name displayed on the menu, 
# because the filename contains no label

# If several macros are doing very similar things, you can just write a 
# main one to handle all cases.  Use callafter=True to ensure the main 
# macro runs after the current one returns.
# In general, you should return a value, and then, the main macro can 
# retrieve it from the 'avsp.Last' variable.
avsp.ExecuteMenuCommand(_('Customized'), callafter=True)
return 59, 54