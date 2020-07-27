from __future__ import print_function

import requests
import json
import os
import pickle
import time
import keyring
from bs4 import BeautifulSoup


"""Bamboo API utilities library.

This library is designed to make interacting with the Bamboo API easier. It has several sub-components.

BambooConnection is a class which wraps connections to the IDM bamboo server. It handles login sessions and basic 
interactions like get requests and downloading files. The easiest way to use it is through the bamboo_connection() 
method which automatically tracks a singleton style instance.

Examples:

    login('user@idmod.org', 'mypassword')

    This logs into the bamboo server and starts a session.
    Without a username and password the login() function will attempt to pull stored credentials via keyring. 
    Credentials can be saved using:
    save_credentials('username', 'password') 
    --
    req = bamboo_connection().make_api_get_request('result/MYPROJ-MYPLAN/123', json=True)
    result_info = json.loads(req.content)

    This makes a git request to the 'result' API with values of 'MYPROJ-MYPLAN' for the plan key and '123' for the build 
    number and indicating the output should be in json format, with the request object as the return value. The output 
    of this API call is then in the .content member of the request which in this case is a plain-text string of json 
    formatted data that can be loaded into a json object via json.loads()  
    --
    The remainder of this module is in the form of classes of static methods providing convenience functions for getting 
    information on builds that have run, build artifacts, and exporting build plans as java specs, check the comments for 
    each class for more information:
        BuildInfo
        BuildArtifacts
        BuildPlans
"""


__DEBUG__ = True

__BAMBOO_CONNECTION__ = None


def bamboo_connection():
    global __BAMBOO_CONNECTION__
    if not __BAMBOO_CONNECTION__:
        __BAMBOO_CONNECTION__ = BambooConnection()
    return __BAMBOO_CONNECTION__


class BambooConnection(object):
    """Bamboo API config and basic functionality/connectivity wrapper.

    Automatically probes the most likely endpoint locations (with and without https, with and without port numbers).

    Important functions:

    - login: logs into the bamboo api, caches the login token so you don't have to pass creds for every req. in a session
    - get_bamboo_api_url: translate a relative API URL into a fully qualified URL
    - normalize_url: detect whether a URL is relative or not, translate relative URLs to fully qualified ones
    - make_get_request: makes a request to the specified API url, adds some convenient error and login handling
    - download_file: downloads a file from the specified artifacts url to a location on disk
    """

    # bamboo end-point parts
    __BAMBOO_SERVER__ = 'idm-bamboo'
    __BAMBOO_PORT__ = '8085'
    __SSL_VERIFY__ = False
    __HTTP__ = 'http://'
    __HTTPS__ = 'https://'
    __DEFAULT_TIMEOUT__ = 30
    __RETRY_WAIT__ = 30
    __LOGIN_RETRIES__ = 3

    # bamboo credentials keyring settings (optional)
    __BAMBOO_API_KEYRING_SVC__ = 'bamboo_api'
    __BAMBOO_API_LOGIN__ = '_api_login_'

    def __init__(self):
        self._server = None
        # allows for a different level of debugging than the whole module
        self.debug = __DEBUG__
        self._session_cookie = None
        self.logged_in = False

    @property
    def server(self) -> str:
        """str: Keeps track of a single instance of the server base url. (e.g. http://idm-bamboo:8085)"""
        if not self._server:
            self._server = self.find_server()
        return self._server

    @property
    def session_cookie(self) -> requests.cookies:
        """str: Automatically load and instance the login session cookie jar."""
        if not self._session_cookie:
            self._session_cookie = self.load_session_cookie()
        return self._session_cookie

    def debug_log(self, msg: str):
        """Print debugging info

        Args:
            msg (str): message to print if debugging is on
        """
        if self.debug:
            print(msg)

    def get_server_url(self, ssl: bool = False, useport: bool = False) -> str:
        """Get a particular variant of the server url w/ or w/o ssl and port (e.g. False/False -> http://idm-bamboo)

        Args:
            ssl (bool): whether to use ssl
            useport (bool): whether to use the port

        Returns:
            str: endpoint url
        """
        server_url = ''

        if ssl:
            server_url += self.__HTTPS__
        else:
            server_url += self.__HTTP__
        server_url += self.__BAMBOO_SERVER__
        if useport:
            server_url += ':' + self.__BAMBOO_PORT__
        return server_url

    def find_server(self) -> str:
        """Explore all possible server urls, return the first one found to exist.

        Returns:
            str: server url
        """
        self.debug_log('Determining bamboo server url...')
        for useSSL in [False, True]:
            for usePort in [False, True]:
                url = self.get_server_url(useSSL, usePort)
                self.debug_log(f'Checking ({url})')
                if self.url_exists(url):
                    self.debug_log(f'Success! Found endpoint: {url}')
                    return url
        raise ConnectionError('Unable to find Bamboo service endpoint url.')

    def url_exists(self, url: str) -> bool:
        """Try a simple get request given an endpoint url, return whether it was successful (code 200).

        Args:
            url (str): url to issue a test request to

        Returns:
            bool: whether or not a request to the url succeeds (w/ status 200)
        """
        try:
            r = requests.get(url, timeout=self.__DEFAULT_TIMEOUT__, verify=self.__SSL_VERIFY__)
            self.debug_log(f'{url} response: {r.status_code}')
            if r.status_code == 200:
                return True
        except Exception:
            # t, v, tb = sys.exc_info()
            # formatted_tb = '\n'.join(traceback.format_tb(tb))
            # self.debug_log(f'{t} exception {v}')
            # self.debug_log(formatted_tb)
            pass
        return False

    @property
    def session_cookie_filename(self) -> str:
        """File where bamboo session cookie is stored.

        Returns:
            str: fully qualified file path of session cookie file
        """
        return os.path.join(os.path.expanduser('~'), '.bamboo_session_cookie')

    def load_session_cookie(self) -> requests.cookies:
        """Load api login session cookies from disk.

        Returns:
            requests.cookies: session cookie jar
        """
        if os.path.exists(self.session_cookie_filename):
            with open(self.session_cookie_filename, 'rb') as session_cookie_file:
                return pickle.load(session_cookie_file)
        else:
            raise FileNotFoundError(f'Unable to load session cookie from {self.session_cookie_filename}, file not found')

    def write_session_cookie(self, cookies: requests.cookies):
        """Write post-login cookies for session to disk."""
        with open(self.session_cookie_filename, 'wb') as session_cookie_file:
            pickle.dump(cookies, session_cookie_file)

    def get_bamboo_url(self, relative_url: str) -> str:
        """Add bamboo server, port, and protocol to bamboo url.

        Args:
            relative_url (str): relative url (artifact link or api url)

        Returns:
            str: fully qualified url
        """
        if relative_url.startswith('/'):
            return f'{self.server}{relative_url}'
        else:
            return f'{self.server}/{relative_url}'

    def get_bamboo_api_url(self, relative_url: str, json: bool = False, params: dict = {}) -> str:
        """
        Get fully qualified bamboo api url from a relative url w/ given json mode and appending all parameters.

        Args:
            relative_url (str): api url (e.g. project/<project-key>)
            json (bool): whether to get results in json format (otherwise, default is xml)
            params (dict): name/value dictionary of query parameters

        Returns:
            str: fully qualified url that a request can be issued against
        """
        url = f'rest/api/latest/{relative_url}'
        if json:
            url += '.json'
        if params:
            url += '?' + '&'.join([f'{name}={val}' for (name, val) in params.items()])
        return self.get_bamboo_url(url)

    def save_credentials(self, username: str, password: str):
        """Save bamboo api login credentials using keyring.

        Args:
            username (str): bamboo api login username (e.g. somebody@idmod.org)
            password (str): bamboo api login password
        """
        keyring.set_password(self.__BAMBOO_API_KEYRING_SVC__, self.__BAMBOO_API_LOGIN__, username)
        keyring.set_password(self.__BAMBOO_API_KEYRING_SVC__, username, password)

    def ensure_logged_in(self):
        """Check if a login session exists using saved cookies, if not login using keyring stored creds."""
        if not self.logged_in:
            if self.login_session_exists():
                self.debug_log('Existing login session found.')
                self.logged_in = True
            else:
                self.debug_log('No existing login session found.')
                self.login()

    def login_session_exists(self) -> bool:
        """Test whether an existing session cookie exists and an active login session exists.

        Returns:
             bool: whether an active login session exists
        """
        try:
            r = self._make_get_request_internal(self.get_bamboo_api_url('project'))
            if r.status_code == 200:
                return True
        except Exception:
            pass
        return False

    def login(self, username: str = None, password=None) -> bool:
        """Login to the bamboo api. If username or password are not provided, use stored credentials from keyring.

        Args:
            username (str): bamboo api login username (e.g. somebody@idmod.org)
            password (str): bamboo api login password

        Returns:
            bool: success/failure
        """
        if not username or not password:
            import keyring
            if not username:
                username = keyring.get_password(self.__BAMBOO_API_KEYRING_SVC__, self.__BAMBOO_API_LOGIN__)
            if not username:
                raise PermissionError('Unable to get credentials for bamboo API.')
            password = keyring.get_password(self.__BAMBOO_API_KEYRING_SVC__, username)
        success = False

        # sometimes the initial login process is slow or fails, allow for retries after a delay
        retries = 0
        while not success:
            try:
                success = self._login_internal(username, password)
                if success:
                    self.logged_in = True
                    return success
            except Exception:
                if retries >= self.__LOGIN_RETRIES__:
                    raise
            time.sleep(self.__RETRY_WAIT__)
            retries += 1

        return success

    def _login_internal(self, username: str = None, password=None) -> bool:
        """Internal implementation of bamboo api login using provided username and password.

        Wraps return values from bamboo w/ more helpful error handling, stores session cookie to disk so api calls in
        the same session don't need to keep providing the username/password.

        Args:
            username (str): bamboo api login username (e.g. somebody@idmod.org)
            password (str): bamboo api login password

        Returns:
            bool: success/failure
        """
        url = f'{self.server}/rest/api/latest/?os_authType=basic'
        self.debug_log(f'Logging in via: {url}')
        r = requests.get(url, auth=(username, password), timeout=self.__DEFAULT_TIMEOUT__, verify=self.__SSL_VERIFY__)
        if r.status_code == 200:
            self.write_session_cookie(r.cookies)
            self._session_cookie = r.cookies
            self.debug_log('Login success!')
            return True
        else:
            if r.status_code == 401:
                raise PermissionError("Bamboo API returned status code 401, unauthorized.")
            raise ValueError("Unable to query bamboo API w/ url '{url}', status code {r.status_code}: {r.content}")
        return False

    def normalize_url(self, url: str) -> str:
        """Determine whether a url is relative or fully qualified, translate relative urls to fully qualified versions.

        Args:
            url (str): relative or fully qualified url

        Returns:
            str: fully qualified url
        """
        if url.startswith(self.__HTTP__) or url.startswith(self.__HTTPS__):
            request_url = url
        else:
            request_url = self.get_bamboo_url(url)
        return request_url

    def make_get_request(self, url: str, retries: int = 3) -> requests.Response:
        """Make a get request against the bamboo server.

        Args:
            url (str): relative or fully qualified url

        Returns:
            requests.Response: request object returned from requests.get()
        """
        self.ensure_logged_in()

        try:
            return self._make_get_request_internal(url)
        except PermissionError:
            self.login()
            return self._make_get_request_internal(url)

    def _make_get_request_internal(self, url: str) -> requests.Response:
        """Make a get request against the bamboo server (do not automatically ensure login).

        Args:
            url (str): relative or fully qualified url

        Returns:
            requests.Response: request object returned from requests.get()
        """
        request_url = self.normalize_url(url)

        self.debug_log(f"Getting url '{request_url}'")
        r = requests.get(request_url, cookies=self.session_cookie, verify=self.__SSL_VERIFY__)
        self.debug_log(f'Status code: {r.status_code}')
        if r.status_code == 401:
            raise PermissionError("Bamboo API returned status code 401, unauthorized.")
        elif r.status_code != 200:
            raise ValueError(f"Unable to query bamboo API w/ url '{url}', status code {r.status_code}: {r.content}")
        if '<title>Log in as a Bamboo user - Bamboo Continuous Integration Build Server</title>' in r.text:
            raise PermissionError('Not logged in to bamboo')

        return r

    def make_api_get_request(self, relative_url: str, json: bool = False, params: dict = {}) -> requests.Response:
        """Translate relative api url to the fully qualified bamboo api url, make a get request against it.

        Args:
            relative_url (str): url relative to the bamboo api endpoint (e.g. 'result/MYPROJ-MYPLAN/123') to make the request against
            json (bool): whether to return results in json
            params (dict): name/value dictionary of additional parameters to pass

        Returns:
            requests.Response: request object returned from requests.get()
        """
        return self.make_get_request(self.get_bamboo_api_url(relative_url, json=json, params=params))

    def download_file(self, url: str, destination: str) -> list:
        """Download a specific artifact file (from the full artifact url provided) to disk.

        Streams the download to avoid common 'gotchas' with downloading via http.

        Args:
            url (str): url to download
            destination (str): destination path or filename where the artifact is to be downloaded to

        Returns:
            (str): local filename of file that has been downloaded
        """
        self.ensure_logged_in()

        destination_filename = destination

        # if a folder instead of a file is provided as a destination, use the filename of the artifact
        if os.path.isdir(destination) or destination.endswith(os.path.sep):
            url_parts = url.split('/')
            if len(url_parts) > 0:
                destination_file = url_parts[-1]
            else:
                destination_file = 'New_File'
            destination_filename = os.path.join(destination, destination_file)

        destination_filename = os.path.abspath(destination_filename)
        dest_folder = os.path.dirname(destination_filename)
        if dest_folder:
            os.makedirs(dest_folder, exist_ok=True)

        download_url = self.normalize_url(url)
        file_req = requests.get(download_url, stream=True, cookies=self.session_cookie, verify=self.__SSL_VERIFY__)

        with open(destination_filename, 'wb') as file:
            self.debug_log(f'Writing downloaded file from {download_url} to file {destination_filename}')
            for chunk in file_req.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        file_req.close()
        return destination_filename


class BuildInfo(object):
    """A collection of methods for getting data on build results."""

    @classmethod
    def build_passed(cls, plan_key: str, build_num: int) -> bool:
        """Determine whether a given build succeeded or not.

        Args:
            plan_key (str): bamboo plan key (including project key)
            build_num (int): build number to retrieve results for

        Returns:
            bool: whether the build succeeded
        """
        req = bamboo_connection().make_api_get_request(f'result/{plan_key}/{build_num}', json=True)
        return cls.successful_build_result(json.loads(req.content))

    @staticmethod
    def successful_build_result(result) -> bool:
        """Analyze a build result json object and determine if it corresponds to a successful build

        Args:
            result: json build result

        Returns:
            bool: whether the build was successful
        """
        if result and 'state' in result:
            _debug_log('Build state: {}'.format(result['state']))
            _debug_log('Build successful')
            return result['state'] == 'Successful'
        return False

    @staticmethod
    def get_build_info(plan_key: str, index: int):
        """Retrieve the build info in json format for a given build plan with a relative index (0=latest)

        Args:
            plan_key (str): bamboo plan key (including project key)
            index (int): index of build to retrieve info for (0=latest, 1=2nd most recent, etc.)

        Returns:
            build info results json
        """
        _debug_log(f"Getting build info for build {plan_key} #{index}")
        req = bamboo_connection().make_api_get_request(f'result/{plan_key}/', json=True,
                                                       params={'expand': f'results%5B{index}%5D.result'})
        req_json = json.loads(req.content)
        if 'results' in req_json:
            results_json = req_json['results']
            if 'result' in results_json:
                if len(results_json['result']) > 0:
                    return results_json['result'][0]
        raise RuntimeError(f'Unable to find build result for {plan_key} at index {index}')

    @classmethod
    def get_latest_successful_build(cls, plan_key: str, scheduled_only: bool = True, max_iterations: int = 50):
        """Find the latest successful build within the last max_iterations builds for a given plan.

        Args:
            plan_key (str): bamboo plan key (including project key)
            scheduled_only (bool): only count automatically run scheduled or triggered builds as successful
            max_iterations (int): maximum number of older builds to look through

        Returns:
            (tuple): tuple containing:
                build_num (str): build number of last successful build
                build_info: json data structure of build info for that build
        """
        # TODO: should probably have a timeout condition or something
        _debug_log(f'Finding latest build for {plan_key}')
        for build_index in range(max_iterations):
            _debug_log(f'Checking build {build_index}')
            build_info = cls.get_build_info(plan_key, build_index)
            _debug_log(f'Build info: {build_info}')
            if cls.successful_build_result(build_info):
                if not scheduled_only:
                    return build_info['buildNumber'], build_info
                elif build_info['buildReason'] == 'Scheduled' or build_info['buildReason'].startswith('Changes by'):
                    _debug_log('Build was scheduled.')
                    return build_info['buildNumber'], build_info
        raise ValueError(f'Could not find a successful build for {plan_key} within the latest {max_iterations} runs.')

    @classmethod
    def get_latest_build(cls, plan_key: str):
        """Get the build info for the most recently run build for a given plan.

        Args:
            plan_key (str): bamboo plan key (including project key)

        Returns:
            (tuple): tuple containing:
                build_num (str): build number of last successful build
                build_info: json data structure of build info for that build
        """
        build_info = cls.get_build_info(plan_key, 0)
        _debug_log(f'Build info: {build_info}')
        return build_info['buildNumber'], build_info


class BuildArtifacts(object):
    """A collection of methods for finding and interacting with build artifacts."""

    @classmethod
    def find_artifacts(cls, plan_key: str, build_num: int, artifact: str) -> list:
        """Find all urls for files of an artifact of a given name for a specific build.

        Args:
            plan_key (str): bamboo plan key (including project key)
            build_num (int): build number to retrieve artifact urls for
            artifact (str): artifact name/id

        Returns:
            (:obj:`list` of :obj:`str`): list of artifact urls that can be downloaded
        """
        artifact = artifact.replace(' ', '-')
        url = f'/artifact/{plan_key}/shared/build-{build_num}/{artifact}'
        _debug_log(f'Getting url {url}')
        return cls._find_artifact_internal(url)

    @classmethod
    def _find_artifact_internal(cls, url: str) -> list:
        """Internal implementation of getting actual artifact urls with a starting artifact url.

        Enumerates all directory entries, drills down into each, returns only the full file urls found.

        Returns:
            (:obj:`list` of :obj:`str`): list of artifact urls that can be downloaded
        """
        result = bamboo_connection().make_get_request(url)
        artifact_soup = BeautifulSoup(result.text, 'html.parser')
        table = artifact_soup.find_all('tr')
        urls = []
        for row in table:
            url, is_file = cls._get_url_from_row(row)
            if is_file:
                urls.append(url)
            elif url:
                urls.extend(cls._find_artifact_internal(url))
        return urls

    @staticmethod
    def _get_url_from_row(table_row) -> str:
        """Internal implementation for retrieving an artifact url for a row of data in the html page of the landing page.

        Args:
            table_row: html of a row entry from the artifact page (BeautifulSoup object)

        Returns:
            str: url of the link on the row
        """
        columns = table_row.find_all('td')
        if len(columns) != 3:
            return (None, None)
        first_url = columns[0].select('a')[0]
        if first_url.get_text().startswith('Parent Directory'):
            return (None, None)
        is_file = columns[0].select('img')[0]['alt'] == '(file)'
        return (first_url['href'], is_file)

    @classmethod
    def download_artifact_to_file(cls, plan_key: str, build_num: int, artifact: str, destination: str) -> list:
        """Download files found for a named artifact to the filepath provided.

        Additional files found will be downloaded as _2, _3, _4, etc. For example, if there are 3 files for
        'Eradication.exe' the first will be Eradication.exe, the second will be Eradication_2.exe, the third
        Eradication_3.exe.

        Args:
            plan_key (str): bamboo plan key (including project key)
            build_num (int): build number to retrieve artifact urls for
            artifact (str): artifact name/id
            destination (str): destination path or filename where the artifact is to be downloaded to

        Returns:
            (:obj:`list` of :obj:`str`): list of local filenames of files that have been downloaded
        """
        artifact_urls = cls.find_artifacts(plan_key, build_num, artifact)
        downloaded_files = []
        if len(artifact_urls) > 0:
            # TODO: add name of artifact from url to log
            downloaded_file = bamboo_connection().download_file(artifact_urls[0], destination)
            downloaded_files.append(downloaded_file)
            _debug_log(f"Downloaded artifact '{artifact}' from build {plan_key}#{build_num} to '{downloaded_file}'")

            if len(artifact_urls) > 1:
                filename_conflict = not os.path.isdir(destination)
                if filename_conflict:
                    base_name = os.path.basename(destination)
                    # note: this code still works when there is no extension
                    name, ext = os.path.splitext(base_name)

                for i in range(1, len(artifact_urls)):
                    filenum = i + 1
                    if filename_conflict:
                        destination_file = os.path.join(destination, f'{name}_{filenum}{ext}')
                    else:
                        destination_file = destination
                    downloaded_file = bamboo_connection().download_file(artifact_urls[i], destination_file)
                    _debug_log(
                        f"Downloaded additional artifact '{artifact}' #{filenum} from build {plan_key}#{build_num} to '{downloaded_file}'")
                    downloaded_files.append(downloaded_file)

        return downloaded_files

    @classmethod
    def download_artifacts_to_path(cls, plan_key: str, build_num: int, artifact: str, destination_path: str) -> list:
        """Download all the files for a given artifact and build to a specific folder, using their original filenames.

        Args:
            plan_key (str): bamboo plan key (including project key)
            build_num (int): build number to retrieve artifact urls for
            artifact (str): artifact name/id
            destination_path (str): path to destination folder where files are to be downloaded

        Returns:
            (:obj:`list` of :obj:`str`): list of local filenames of files that have been downloaded
        """
        artifact_urls = cls.find_artifacts(plan_key, build_num, artifact)
        downloaded_files = []
        for url in artifact_urls:
            downloaded_file = bamboo_connection().download_file(url, destination_path)
            _debug_log(f"Downloaded file from artifact (artifact) from build {plan_key}#{build_num} to '{downloaded_file}'")
            downloaded_files.append(downloaded_file)

        return downloaded_files

    @classmethod
    def download_latest_good_Eradication_exe(cls, plan_key: str, destination: str) -> str:
        """Find the latest successful build for a specified plan, download the Eradication.exe artifact to a specified path.

        Args:
            plan_key (str): bamboo plan key (including project key)
            destination (str): destination path or filename where the artifact is to be downloaded to

        Returns:
            str: build number of build that was found and had its Eradication artifact downloaded
        """
        (build_num, build_info) = BuildInfo.get_latest_successful_build(plan_key)
        artifact_urls = cls.find_artifacts(plan_key, build_num, 'Eradication.exe')
        if len(artifact_urls) > 0:
            bamboo_connection().download_file(artifact_urls[0], destination)
        return build_num

    @classmethod
    def download_from_bamboo_url(cls, url: str, destination: str):
        """
        Download Eradication.exe/Eradication directly from bamboo url
        Assume you already done login

        Args:
            url
            destination (str): destination path or filename where the artifact is to be downloaded to

        Returns:
            str: local file path that have been downloaded
        """
        downloaded_file = bamboo_connection().download_file(url, destination)
        _debug_log("Downloaded from bamboo artifact url")
        return downloaded_file


class BuildPlans(object):
    """Collection of methods for getting information on build plans."""

    @staticmethod
    def export_spec(plan_key: str) -> str:
        """Export a specific build plan to java specs.

        Args:
            plan_key (str): bamboo plan key (including project key)

        Returns:
            str: full text of the .java file for the plan spec, if the plan was found (empty string if not)
        """
        url = 'exportSpecs/plan.action?buildKey=' + plan_key
        export_req = bamboo_connection().make_get_request(url)
        if export_req and export_req.status_code == 200:
            soup = BeautifulSoup(export_req.text, 'html.parser')
            specs_textarea = soup.find('textarea', {'name': 'exportItem'})
            if specs_textarea:
                return specs_textarea.text
        return ''

    @staticmethod
    def get_plans_for_project(project_key: str) -> list:
        """Return a list of all the build plans for every plan in the project.

        Args:
            project_key (str): bamboo project key

        Returns:
            (:obj:`list` of :obj:`str`): list of plan keys for each plan that was found in the project
        """
        plans = []
        r = bamboo_connection().make_api_get_request(f'project/{project_key}', json=True, params={'expand': 'plans'})
        if r and r.status_code == 200:
            rjson = json.loads(r.text)
            if 'plans' in rjson and 'plan' in rjson['plans']:
                plans_json = rjson['plans']['plan']
                for plan in plans_json:
                    plans.append(plan['key'])
        return plans


# -----------------------------
def _debug_log(message):
    """Simple debug logging convenience function.

    :param message: message to print if debugging is on.
    """
    if __DEBUG__:
        print(f'DEBUG: {message}')


def set_debug(debug: bool):
    """Set debugging messaging level for module.

    Args:
        debug (bool): turn on or off debugging messages
    """
    bamboo_connection().debug = debug
    global __DEBUG__
    __DEBUG__ = debug


def login(username=None, password=None):
    """Pass through to BambooConnection.login()"""
    bamboo_connection().login(username, password)


def save_credentials(username, password):
    """Pass through to BambooConnection.save_credentials()"""
    bamboo_connection().save_credentials(username, password)
