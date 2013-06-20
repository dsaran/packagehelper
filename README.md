Package Helper
===

- *Info:*  A release automation tool (for reference only)
- *Author:* Daniel Saran



About
---

This is graphical tool I created to automate release process in my previous job.

What the application does is to checkout a bunch of tagged SQL files from a CVS or SVN repository and create an install script.

It assumes the sql files are located in the directory structure below:
- DB_NAME/DB_SCHEMA/SCRIPT_TYPE/filename.sql
 (e.g. DB1/SOME_USER/IDX/some_index.sql)

With this, the application will create an install script for each DB-SCHEMA combination calling the original scripts (ex: 001_SCHEMA_DBNAME.sql)
The *SCRIPT_TYPE* is used only to define the order in which each script will be called from the install script (ex: a create table should be called before index creation)



Technology
---
This tool was written in Python with Kiwi+GTK and using Gazpacho for the GUI design.
The dependencies (Kiwi, Gazpacho, etc) were embedded in the application code to make it more portable.


Note
---
This application probably won't be useful for anyone outside this specific company as it is based on a very specific directory structure and process for creating a release package.

The code was published only to serve as reference.

The tool was written entirely by myself outside the company so this doesn't hurt any NDA clause.
