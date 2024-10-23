# tidsreg

The missing tool for registrering time in the municipality of Copenhagen.

# Installation

```bash
pip install tidsreg
```
or
```bash
uv tool install tidsreg
```

# Getting started
First, make sure that `tidsreg` is configured and log in through the browser.
```bash
tidsreg init
tidsreg login
```

Then add, show or clear registrations:
```bash
tidsreg show
tidsreg add <projectname> -s 9 -e 1015 -m "A comment"
tidsreg clear  # WILL DELETE YOUR REGISTRATIONS!
```



# TODO
* Guide til autocomplete: https://click.palletsprojects.com/en/8.1.x/shell-completion/
* Change author email: https://stackoverflow.com/questions/750172/how-do-i-change-the-author-and-committer-name-email-for-multiple-commits
* Look into releases on github and setup a pipeline (Actions)
* Make adding registrations wait for the list to update (expect(thelist).to_have_count(thecount) - make it optional to speed up processing when making many registrations
* Check if a registration can be made without trying in the browser
* Add no-trunc flag to show command after it has been prettyfied
* Implement functionality to change date
* Export of current registrations to bulk-file
