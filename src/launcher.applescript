use framework "Foundation"
use framework "AppKit"
use scripting additions

on run
    -- Force this application to the front and grab keyboard focus
    tell current application to activate
    current application's NSApplication's sharedApplication()'s activateIgnoringOtherApps:true

    set appTitle to "codep"
    
    -- Prompt for folder name or search terms
    try
        set dialogResult to display dialog "Enter project name, keywords, or path:" default answer "" with title appTitle buttons {"Cancel", "Open"} default button "Open"
        set folderQuery to text returned of dialogResult
    on error
        return
    end try

    if folderQuery is "" then
        return
    end if

    -- Locate internal python resolver
    set myPath to POSIX path of (path to me)
    set pyScript to myPath & "Contents/Resources/resolver.py"

    -- Run resolver script
    set pyCmd to "/usr/bin/python3 " & quoted form of pyScript & " " & quoted form of folderQuery
    try
        set searchOutput to do shell script pyCmd
    on error errMsg
        tell current application to activate
        current application's NSApplication's sharedApplication()'s activateIgnoringOtherApps:true
        display alert "Search error" message errMsg as critical
        return
    end try

    if searchOutput is "" then
        tell current application to activate
        current application's NSApplication's sharedApplication()'s activateIgnoringOtherApps:true
        display alert "No project found" message "Could not find any matches for \"" & folderQuery & "\"." as warning
        return
    end if

    set outputLines to paragraphs of searchOutput
    
    -- Parse EDITOR line
    set targetEditor to "Visual Studio Code"
    set lineIdx to 1
    if (count of outputLines) >= 1 then
        set firstLine to item 1 of outputLines
        if firstLine starts with "EDITOR:" then
            set targetEditor to text 8 thru -1 of firstLine
            set lineIdx to 2
        end if
    end if

    if (count of outputLines) < lineIdx then
        return
    end if

    set modeLine to item lineIdx of outputLines
    set dataStart to lineIdx + 1

    if modeLine is "MODE:SINGLE" then
        if (count of outputLines) >= dataStart then
            set targetPath to item dataStart of outputLines
            do shell script "open -a " & quoted form of targetEditor & " " & quoted form of targetPath
        end if
    else if modeLine is "MODE:MULTIPLE" or modeLine is "MODE:APPROX" then
        if (count of outputLines) < dataStart then
            tell current application to activate
            current application's NSApplication's sharedApplication()'s activateIgnoringOtherApps:true
            display alert "No project found" message "Could not find any matches for \"" & folderQuery & "\"." as warning
            return
        end if

        set candidateList to items dataStart thru -1 of outputLines
        
        if modeLine is "MODE:MULTIPLE" then
            set promptText to "Found multiple matches for \"" & folderQuery & "\":"
        else
            set promptText to "No exact match for \"" & folderQuery & "\". Did you mean:"
        end if

        tell current application to activate
        current application's NSApplication's sharedApplication()'s activateIgnoringOtherApps:true
        
        set chosen to choose from list candidateList with prompt promptText default items {item 1 of candidateList} with title appTitle OK button name "Open"
        
        if chosen is not false then
            set chosenPath to item 1 of chosen
            set homeDir to POSIX path of (path to home folder)
            if chosenPath starts with "~/" then
                set targetPath to homeDir & (text 3 thru -1 of chosenPath)
            else
                set targetPath to chosenPath
            end if
            do shell script "open -a " & quoted form of targetEditor & " " & quoted form of targetPath
        end if
    else
        tell current application to activate
        current application's NSApplication's sharedApplication()'s activateIgnoringOtherApps:true
        display alert "No project found" message "Could not find any matching or approximate folders for \"" & folderQuery & "\"." as warning
    end if
end run
