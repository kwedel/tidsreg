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

# Bulk registrations
It is possible to register multiple items at the same time using the `bulk` command.
Create a file with `<TAB>` between the time, the project, and the optional comment and pass it using the `-f` option.

```
$ cat bulkfile
830	project1	Optional comment
9	project2
1130	frokost
12
14:00	project1	Another comment
1415
$ tidsreg bulk -f bulkfile
```
Whis will create four registrations:
* project1 from 8:30 to 9:00
* project2 from 9:00 to 11:30
* frokost from 11:30 to 12:00
* project1 from 14:00 to 14:15

# Headless login
By setting the environement variables `TIDSREG_USERNAME` and `TIDSREG_PASSWORD`, it is possible to login headlessly by adding the `--headless` option to the `tidsreg login` command.

# Autocomplete
Follow this guide to setup autocomplete: https://click.palletsprojects.com/en/8.1.x/shell-completion/

# Development
When things don't work, call `tidsreg` with `PWDEBUG=1` to follow along in the browser.

# TODO
* Look into releases on github and setup a pipeline (Actions)
* Make adding registrations wait for the list to update (expect(thelist).to_have_count(thecount) - make it optional to speed up processing when making many registrations
* Check if a registration can be made without trying in the browser
* Add no-trunc flag to show command after it has been prettyfied
* Export of current registrations to bulk-file
