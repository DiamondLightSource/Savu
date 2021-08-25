
How to test savu plugin
--------------------------------------

Tunhe Zhou

.. raw:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Tunhe Zhou : How to test savu plugin</title>
            <link rel="stylesheet" href="styles/site.css" type="text/css" />
            <META http-equiv="Content-Type" content="text/html; charset=UTF-8">
        </head>

        <body class="theme-default aui-theme-default">
            <div id="page">
                <div id="main" class="aui-page-panel">

                    <div id="content" class="view">
                        <div class="page-metadata">


                            </div>
                        <div id="main-content" class="wiki-content group">
                        <ol><li>set github local repository, follow this instruction: <a class="external-link" href="https://savu.readthedocs.io/en/latest/dev_guides/dev_github/" rel="nofollow">https://savu.readthedocs.io/en/latest/dev_guides/dev_github/</a></li><li>make the plugins in the folder of plugin, for example: hilbert_filter.py</li><li>change the savu path to the github savu folder:<br/>export SAVUHOME=/home/btq48787/github/Savu</li><li>then <br/>module load savu<br/>savu_config<br/>list<br/>the new plugin should show in the list</li><li>create a simple process list, for example with only NxtomoLoader and the new plugin. save it outside the github folder somewhere.</li><li>run savu with the test process list and test data in /home/btq48787/github/Savu/test_data/data/24737.nxs</li><li>If everything is fine. Open an example test file in /home/btq48787/github/Savu/savu/test/travis/plugin_tests/filter_tests<br/>Use it as template to make a process_test python file for the new plugin.<br/>save the process_list nxs file to /home/btq48787/github/Savu/test_data/test_process_lists<br/>in terminal window:<br/>test_setup.sh<br/>python the_new_process_test.py<br/>If it runs through, then it's fine. We can push it on to github.</li><li>git status<br/>it should show that we have 3 more files now: one python for new plugin, one nxs for process list, one python for test plugin<br/>git add all the files<br/>git status<br/>they should look green now<br/>git commit -m &quot;message for the change&quot;<br/>git pull upstream master<br/>to update to the newest version from the diamond light source. If there were a lot of changes. might need to test again to see if the plugin works<br/>git push origin master<br/>push the changes to the master branch of my fork.</li><li>on github webpage, pull request to diamond for changes <br/><br/></li></ol><p><br/></p>
                        </div>



                    </div>             </div>

            </div>     </body>
    </html>
