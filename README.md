TestON, a testing infastructure by Paxterra and Open Networking Labs
=======================================
TestON is the testing platform that all the ONOS tests are being run on currently.


Code Style
-------------
At ON.Lab, we have adopted the [Mininet Python style](https://github.com/mininet/mininet/wiki/Mininet-Python-Style) for our drivers and testcases. The one exception is that TestON does not correctly parse multiline comments in testcases when the ending triple double quotes are on the same line as the comment. Therefore, in the testcases, the ending triple double quotes must be on it's own line.


Setup
-------------

0. Pull the git repo from gerrit or github(Read only mirror)

    $ git clone https://gerrit.onosproject.org/OnosSystemTest

    or

    $ git clone https://github.com/OPENNETWORKINGLAB/OnosSystemTest.git

1. Run the install script

    $ cd OnosSystemTest/TestON

    $ install.sh



Dependencies
------------
1. ONOS - The system under test

2. [Mininet](https://github.com/mininet/mininet) - A Network Emulator. NOTE: Some driver functions rely on a modified version of Mininet. These functions are noted in the mininet driver file. To checkout this branch from your Mininet folder:

    $ git remote add jhall11 https://github.com/jhall11/mininet.git

    $ git fetch jhall11

    $ git checkout -b dynamic_topo remotes/jhall11/dynamic_topo

    $ git pull

    Note that you may need to run 'sudo make develop' if your mnexec.c file changed when switching branches.

3. There are some python modules required by some test cases. These modules should be installed when running the install.sh script.

4. Linc-OE - Some testcases use this to emulate optical devices

    Requirements:

    1. Erlang R15B, R16B, R17 - if possible please use R17

      $ sudo apt-get install erlang

    2. libpcap-dev package if eth interfaces will be used

      $ sudo apt-get install libpcap-dev

    Building and Running:

    $ git clone https://github.com/shivarammysore/LINC-Switch.git linc-oe

    $ cd linc-oe

    $ git checkout tags/oe-0.3

    $ cp rel/files/sys.config.orig rel/files/sys.config

    $ make rel

Configuration
------------

1. Config file at TestON/config/teston.cfg

    Change the file paths to the appropriate paths

2. The .topo file for each test

    Must change the IPs/login/etc to point to the nodes you want to run on

Running TestON
------------

1. TestON must be ran from its bin directory

    $ cd TestON/bin

2. Launch cli

    $ ./cli.py

3. Run the test

    $ teston run SAMPstartTemplate_1node

The Tests
-----------------------------------------------

The tests are all located it TestON/tests/
Each test has its own folder with the following files:

1. .ospk file (optional)

    - This is written in Openspeak, a word based language developed by Paxterra.

    - It defines the cases and sequence of events for the test

    - TestON will automatically generate the .py file based on the .ospk file if the .ospk file exists.

2. .py file

    - This file serves the same exact function as the openspeak file.

    - It will only be used if there is NO .ospk file, so if you like python, delete or rename the .ospk file

3. .topo file

    - This defines all the components that TestON creates for that test and includes data such as IP address, login info, and device drivers

    - The Components must be defined in this file to be uesd in the openspeak or python files.

4. .params file

    - Defines all the test-specific variables that are used by the test.

    - NOTE: The variable `testcases` defines which testcases run when the test is ran.

Troubleshooting
-----------------------------------------------
Here are a few things to check if it doesn't work

1. Double check the topo file for that specific test the nodes must be able to run that specific component ( Mininet IP -> machine with mn installed)

2. Enable passwordless logins between your nodes and the TestON node.

Features
-----------------------------------------------
Some features in TestON are:

- Pause Function

- [Retry Function](TestON/Documentation/features/retry.md)

- Test suite hierarchy

- Test dependency folders

- 

- 

- 

- 
