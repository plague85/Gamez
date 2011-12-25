import cherrypy
import json
import os
from DBFunctions import GetWiiGamesFromTerm, GetWiiGameDataFromTerm, AddWiiGameToDb, GetRequestedGames, RemoveWiiGameFromDb, UpdateStatus, GetLog, ClearDBLog
from UpgradeFunctions import CheckForNewVersion,IgnoreVersion,UpdateToLatestVersion
import ConfigParser
from time import sleep
import urllib

class WebRoot:
    appPath = ''

    def __init__(self,app_path):
        WebRoot.appPath = app_path

    @cherrypy.expose
    def index(self,status_message='',version=''):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        html = """

        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
          <head>
            <link rel="stylesheet" type="text/css" href="css/navigation.css" />
            <link rel="stylesheet" type="text/css" href="css/redmond/jquery-ui-1.8.16.custom.css" />
            <link rel="stylesheet" type="text/css" href="css/datatables.css" />
            <link rel="stylesheet" type="text/css" href="css/jquery.ui.override.css" />
            <script type="text/javascript" src="js/jquery-1.6.2.min.js"></script>
            <script type="text/javascript" src="js/jquery-ui-1.8.16.custom.min.js"></script>
            <script type="text/javascript" src="js/menu.js"></script>
            <script type="text/javascript" language="javascript" src="/js/jquery.dataTables.min.js"></script>
          </head>
          <body id="dt_example">"""
        if(status_message <> ''):
            html = html + """
                            <div id='_statusbar' class='statusbar statusbarhighlight'>""" + status_message + """</div>"""
        isNewVersionAvailable = CheckForNewVersion(WebRoot.appPath)
        if(isNewVersionAvailable):
            html = html + """
                            <div id='_statusbar' class='statusbar statusbarhighlight'>New Version Available :: <a href="/upgradetolatestversion?verification=SYSTEM_DIRECTED">Upgrade Now</a> | <a href="/ignorecurrentversion?verification=SYSTEM_DIRECTED">Ignore Until Next Version</a></div>
                          """
        html = html + """
            <div id="menu">
                <ul class="menu">
                    <li class="parent">
                        <a href="/">
                            Home
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/settings">
                            Settings
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/log">
                            Log
                        </a>
                    </li>
                </ul>
                <div style="text-align:right;margin-right:20px">
                    <div class=ui-widget>
                        <INPUT id=search />
                        &nbsp;
                        <button style="margin-top:8px" id="searchButton" class="ui-widget" style="font-size:15px" name="searchButton" type="submit">Search</button> 
                        <script>
                            $("#search").autocomplete(
                                {
                                    source:"/get_wii_game_list/",
                                    minChars: 1,
                                    max:25,
                                    dataType:'json'
                                }
                            );
                            $("button").button().click(function(){
                                var searchText = document.getElementById("search").value;
                                //alert(searchText);
                                document.location.href = "search?term=" + searchText;
                            });
                        </script>
                    </div>
                </div>
            </div>
            <div style="visibility:hidden"><a href="http://apycom.com/">jQuery Menu by Apycom</a></div>
            <div id="container">"""
        db_result = GetRequestedGames()
        if(db_result == ''):
            html  = html + """No games added. Try searching for some."""
        else:
            html = html + """
                <script>function UpdateGameStatus(status,db_id){var redirectUrl = '/updatestatus?game_id=' + db_id + '&status=' + status;location.href=redirectUrl;}</script>
              <table cellpadding="0" cellspacing="0" border="0" class="display" id="searchresults">
                <thead>
                  <tr>
                    <th>Actions</th>
                    <th>Game Name</th>
                    <th>Game ID</th>
                    <th>Status</th>
                    <th>Update Status</th>
                  </tr>
                </thead>
                <tbody>"""
            html = html + db_result
            html = html + """
                </tbody>
              </table>
              <script>$(document).ready(function() {
	            oTable = $('#searchresults').dataTable({"bJQueryUI": true,"bSort":false,"bLengthChange":false});});
              </script>
             """
        html = html + """
            </div>
          </body>
        </html>
        

               """
        return html;

    @cherrypy.expose
    def search(self,term=''):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        html = """

        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
          <head>
            <link rel="stylesheet" type="text/css" href="css/navigation.css" />
            <link rel="stylesheet" type="text/css" href="css/redmond/jquery-ui-1.8.16.custom.css" />
            <link rel="stylesheet" type="text/css" href="css/datatables.css" />
            <link rel="stylesheet" type="text/css" href="css/jquery.ui.override.css" />
            <script type="text/javascript" src="js/jquery-1.6.2.min.js"></script>
            <script type="text/javascript" src="js/jquery-ui-1.8.16.custom.min.js"></script>
            <script type="text/javascript" src="js/menu.js"></script>
            <script type="text/javascript" language="javascript" src="/js/jquery.dataTables.min.js"></script>
          </head>
          <body id="dt_example">
            <div id="menu">
                <ul class="menu">
                    <li class="parent">
                        <a href="/">
                            Home
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/settings">
                            Settings
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/log">
                            Log
                        </a>
                    </li>
                </ul>
               <div style="text-align:right;margin-right:20px">
                    <div class=ui-widget>
                        <INPUT id=search />
                        &nbsp;
                        <button style="margin-top:8px" id="searchButton" class="ui-widget" style="font-size:15px" name="searchButton" type="submit">Search</button> 
                        <script>
                            $("#search").autocomplete(
                                {
                                    source:"/get_wii_game_list/",
                                    minChars: 1,
                                    max:25,
                                    dataType:'json'
                                }
                            );
                            $("button").button().click(function(){
                                var searchText = document.getElementById("search").value;
                                //alert(searchText);
                                document.location.href = "search?term=" + searchText;
                            });
                        </script>
                    </div>
                </div>
            </div>
            <div style="visibility:hidden"><a href="http://apycom.com/">jQuery Menu by Apycom</a></div>
            <div id="container">"""
        db_result = GetWiiGameDataFromTerm(term)
        if(db_result == ''):
            html  = html + """No Results Found. Try Searching Again"""
        else:
            html = html + """
              <table cellpadding="0" cellspacing="0" border="0" class="display" id="searchresults">
                <thead>
                  <tr>
                    <th>Download</th>
                    <th>Game Name</th>
                    <th>Game ID</th>
                  </tr>
                </thead>
                <tbody>"""
            html = html + db_result
            html = html + """
                </tbody>
              </table>
              <script>$(document).ready(function() {
	            oTable = $('#searchresults').dataTable({"bJQueryUI": true,"bSort":false,"bLengthChange":false});});
              </script>
             """
        html = html + """
            </div>
          </body>
        </html>
        

               """
        return html;

    @cherrypy.expose
    def settings(self):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        config = ConfigParser.RawConfigParser()
        configFilePath = os.path.join(WebRoot.appPath,'Gamez.ini')
        config.read(configFilePath)
        html = """

        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
          <head>
            <link rel="stylesheet" type="text/css" href="css/navigation.css" />
            <link rel="stylesheet" type="text/css" href="css/redmond/jquery-ui-1.8.16.custom.css" />
            <link rel="stylesheet" type="text/css" href="css/datatables.css" />
            <link rel="stylesheet" type="text/css" href="css/jquery.ui.override.css" />
            <link rel="stylesheet" type="text/css" href="css/settings.css" />
            <script type="text/javascript" src="js/jquery-1.6.2.min.js"></script>
            <script type="text/javascript" src="js/jquery-ui-1.8.16.custom.min.js"></script>
            <script type="text/javascript" src="js/menu.js"></script>
            <script type="text/javascript" language="javascript" src="/js/jquery.dataTables.min.js"></script>
          </head>
          <body id="dt_example">
            <div id="menu">
                <ul class="menu">
                    <li class="parent">
                        <a href="/">
                            Home
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/settings">
                            Settings
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/log">
                            Log
                        </a>
                    </li>
                </ul>
                <div style="text-align:right;margin-right:20px">
                    <div class=ui-widget>
                        <INPUT id=search />
                        &nbsp;
                        <button style="margin-top:8px" id="searchButton" class="ui-widget" style="font-size:15px" name="searchButton" type="submit">Search</button> 
                        <script>
                            $("#search").autocomplete(
                                {
                                    source:"/get_wii_game_list/",
                                    minChars: 1,
                                    max:25,
                                    dataType:'json'
                                }
                            );
                            $("button").button().click(function(){
                                var searchText = document.getElementById("search").value;
                                //alert(searchText);
                                document.location.href = "search?term=" + searchText;
                            });
                        </script>
                    </div>
                </div>
            </div>
            <div style="visibility:hidden"><a href="http://apycom.com/">jQuery Menu by Apycom</a></div>
            <div id="stylized" class="myform">
                <form id="form" name="form" method="get" action="/savesettings">
                <h1>General</h1>

                <label>Gamez Host</label>
                <input type="text" name="cherrypyHost" id="cherrypyHost" value='""" + config.get('global','server.socket_host').replace('"','') +  """' />

                <label>Gamez Port</label>
                <input type="text" name="cherrypyPort" id="cherrypyPort" value='""" + config.get('global','server.socket_port').replace('"','') +  """' />

                <label>Download Interval (In Seconds)</label>
                <input type="text" name="downloadInterval" id="downloadInterval" value='""" + config.get('Scheduler','download_interval').replace('"','') +  """' />

                <h1>SABnzbd+</h1>

                <label>SABnzbd+ Host</label>
                <input type="text" name="sabHost" id="sabHost" value='""" + config.get('Sabnzbd','host').replace('"','') +  """' />

                <label>SABnzbd+ Port</label>
                <input type="text" name="sabPort" id="sabPort" value='""" + config.get('Sabnzbd','port').replace('"','') +  """' />

                <label>SABnzbd+ API Key</label>
                <input type="text" name="sabApi" id="sabApi" value='""" + config.get('Sabnzbd','api_key').replace('"','') +  """' />

                <h1>NZB Matrix</h1>

                <label>NZB Matrix API Key</label>
                <input type="text" name="nzbMatrixApi" id="nzbMatrixApi" value='""" + config.get('NZBMatrix','api_key').replace('"','') +  """' />

                <label>NZB Matrix Username</label>
                <input type="text" name="nzbMatrixUsername" id="nzbMatrixUsername" value='""" + config.get('NZBMatrix','username').replace('"','') +  """' />

                <button type="submit">Save Settings</button>
                <div class="spacer"></div>

                
                </form>
            </div>



          </body>
        </html>
        

               """
        return html;

    @cherrypy.expose
    def log(self,status_message='',version=''):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        html = """

        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
          <head>
            <link rel="stylesheet" type="text/css" href="css/navigation.css" />
            <link rel="stylesheet" type="text/css" href="css/redmond/jquery-ui-1.8.16.custom.css" />
            <link rel="stylesheet" type="text/css" href="css/datatables.css" />
            <link rel="stylesheet" type="text/css" href="css/jquery.ui.override.css" />
            <script type="text/javascript" src="js/jquery-1.6.2.min.js"></script>
            <script type="text/javascript" src="js/jquery-ui-1.8.16.custom.min.js"></script>
            <script type="text/javascript" src="js/menu.js"></script>
            <script type="text/javascript" language="javascript" src="/js/jquery.dataTables.min.js"></script>
          </head>
          <body id="dt_example">"""
        html = html + """
            <div id="menu">
                <ul class="menu">
                    <li class="parent">
                        <a href="/">
                            Home
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/settings">
                            Settings
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/log">
                            Log
                        </a>
                    </li>
                </ul>
                <div style="text-align:right;margin-right:20px">
                    <div class=ui-widget>
                        <INPUT id=search />
                        &nbsp;
                        <button style="margin-top:8px" id="searchButton" class="ui-widget" style="font-size:15px" name="searchButton" type="submit">Search</button> 
                        <script>
                            $("#search").autocomplete(
                                {
                                    source:"/get_wii_game_list/",
                                    minChars: 1,
                                    max:25,
                                    dataType:'json'
                                }
                            );
                            $("button").button().click(function(){
                                var searchText = document.getElementById("search").value;
                                //alert(searchText);
                                document.location.href = "search?term=" + searchText;
                            });
                        </script>
                    </div>
                </div>
            </div>
            <div style="visibility:hidden"><a href="http://apycom.com/">jQuery Menu by Apycom</a></div>
            <div id="container">"""
        db_result = GetLog()
        if(db_result == ''):
            html  = html + """No log entries."""
        else:
            html = html + """
                <script>function UpdateGameStatus(status,db_id){var redirectUrl = '/updatestatus?game_id=' + db_id + '&status=' + status;location.href=redirectUrl;}</script>
              <table cellpadding="0" cellspacing="0" border="0" class="display" id="searchresults">
                <thead>
                    <th>Message</th>
                    <th>Date / Time</th>
                  </tr>
                </thead>
                <tbody>"""
            html = html + db_result
            html = html + """
                </tbody>
              </table>
              <div style="float:right;"><button name="clearLogBtn" id="clearLogBtn" class="clear-log-button" onclick="location.href='/clearlog'">Clear Log</button></div>
              <script>$(document).ready(function() {
	            oTable = $('#searchresults').dataTable({"bJQueryUI": true,"bSort":false,"bLengthChange":false});});
              </script>
             """
        html = html + """
            </div>
          </body>
        </html>
        

               """
        return html;

    @cherrypy.expose
    def updatestatus(self,game_id='',status=''):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        if(status <> ''):
            UpdateStatus(game_id,status)
        raise cherrypy.InternalRedirect('/')

    @cherrypy.expose
    def get_wii_game_list(self,term=''):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        return GetWiiGamesFromTerm(term)

    @cherrypy.expose
    def addgame(self,dbid): 
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        AddWiiGameToDb(dbid,'Wanted')
        raise cherrypy.InternalRedirect('/')

    @cherrypy.expose
    def removegame(self,dbid):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        RemoveWiiGameFromDb(dbid)
        raise cherrypy.InternalRedirect('/')

    @cherrypy.expose
    def ignorecurrentversion(self,verification):
        if(verification == "SYSTEM_DIRECTED"):
            IgnoreVersion(WebRoot.appPath)
        raise cherrypy.InternalRedirect('/') 

    @cherrypy.expose
    def upgradetolatestversion(self,verification):
        if(verification == "SYSTEM_DIRECTED"):
            status = UpdateToLatestVersion(WebRoot.appPath)
            raise cherrypy.InternalRedirect("/?status_message=" + status)

    @cherrypy.expose
    def savesettings(self,cherrypyHost='', nzbMatrixUsername='', downloadInterval=3600, sabPort='', nzbMatrixApi='', sabApi='', cherrypyPort='', sabHost=''):
        cherrypyHost = '"' + cherrypyHost + '"'
        nzbMatrixUsername = '"' + nzbMatrixUsername + '"'
        nzbMatrixApi = '"' + nzbMatrixApi + '"'
        sabApi = '"' + sabApi + '"'
        sabHost = '"' + sabHost + '"'
        config = ConfigParser.RawConfigParser()
        configFilePath = os.path.join(WebRoot.appPath,'Gamez.ini')
        config.read(configFilePath)
        config.set('global','server.socket_host',cherrypyHost)
        config.set('global','server.socket_port',cherrypyPort)
        config.set('NZBMatrix','username',nzbMatrixUsername)
        config.set('NZBMatrix','api_key',nzbMatrixApi)
        config.set('Sabnzbd','host',sabHost)
        config.set('Sabnzbd','port',sabPort)
        config.set('Sabnzbd','api_key',sabApi)
        config.set('Scheduler','download_interval',downloadInterval)
        with open(configFilePath,'wb') as configFile:
            config.write(configFile)
        status = "Application Settings Updated Successfully. Gamez is restarting. If after 5 seconds, Gamez isn't working, update the Gamez.ini file and re-launch Gamez"
        raise cherrypy.InternalRedirect("/?status_message=" + status)

    @cherrypy.expose
    def clearlog(self):
        ClearDBLog()
        raise cherrypy.InternalRedirect('/') 