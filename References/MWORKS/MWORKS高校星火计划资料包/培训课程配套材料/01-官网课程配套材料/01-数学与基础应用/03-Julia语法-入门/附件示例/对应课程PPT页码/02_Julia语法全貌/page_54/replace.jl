if Sys.iswindows()
    path = replace("folder/subfolder/file.txt", "/" => "\\")
else
    path = "folder/subfolder/file.txt"
end
