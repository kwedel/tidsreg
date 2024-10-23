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
* Add metadata fields to pyproject.toml (author, urls, etc. https://packaging.python.org/en/latest/tutorials/packaging-projects/#configuring-metadata )
* Look into releases on github and setup a pipeline (Actions)
* Make adding registrations wait for the list to update (expect(thelist).to_have_count(thecount) - make it optional to speed up processing when making many registrations
* Check if a registration can be made without trying in the browser
* Add bulk subcommand to make many registrations
* Prettify outuput from showcommand
* Add no-trunc flag to show command after it has been prettyfied
* Implement functionality to change date
